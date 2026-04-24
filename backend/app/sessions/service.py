from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session as DBSession

from app.db.models.availability import Availability, UnavailableSlot
from app.db.models.session import Session as SessionModel
from app.db.models.subject import MentorSubject, Subject
from app.db.models.user import User
from app.sessions.exceptions import (
    MentorUnavailableException,
    SessionConflictException,
    SessionNotFoundException,
    UnauthorizedSessionActionException,
)
from app.sessions.matching import build_matcher
from app.sessions.repository import SessionRepository
from app.sessions.state_machine import SessionStateMachine


# ---------------------------------------------------------------------------
# Observer interface (for Daniel's notifications module)
# ---------------------------------------------------------------------------

class SessionEventObserver:
    """
    Observer Pattern — abstract observer interface.

    SOLID - OCP:
    # OCP: New observers can be added without modifying SessionService.

    OOP Abstraction: defines the contract all observers must satisfy.
    OOP Polymorphism: each observer implements handlers differently.
    """

    def on_session_requested(self, session: SessionModel) -> None:
        """Called when a student submits a new session request."""

    def on_session_confirmed(self, session: SessionModel) -> None:
        """Called when a mentor confirms a session."""

    def on_session_declined(self, session: SessionModel) -> None:
        """Called when a mentor declines a session."""

    def on_session_completed(self, session: SessionModel) -> None:
        """Called when a session is marked completed."""

    def on_session_cancelled(self, session: SessionModel) -> None:
        """Called when a session is cancelled by either party."""


# ---------------------------------------------------------------------------
# Session Service
# ---------------------------------------------------------------------------

class SessionService:
    """
    Core booking business logic.

    SOLID - SRP:
    # SRP: Handles only session booking logic.
    #      DB access → SessionRepository.
    #      Notification dispatch → registered observers.
    #      Matching → strategy pattern.

    SOLID - DIP:
    # DIP: Depends on SessionRepository abstraction, not raw SQLAlchemy queries.

    OOP Encapsulation: internal helpers are private.
    """

    def __init__(self, db: DBSession) -> None:
        self._repo = SessionRepository(db)
        self._db = db
        self._observers: List[SessionEventObserver] = []

    # ------------------------------------------------------------------
    # Observer registration
    # ------------------------------------------------------------------

    def register_observer(self, observer: SessionEventObserver) -> None:
        self._observers.append(observer)

    def _notify(self, event: str, session: SessionModel) -> None:
        """
        Observer Pattern — notify all registered observers.
        OOP Polymorphism: each observer handles events differently.
        """
        for observer in self._observers:
            handler = getattr(observer, event, None)
            if callable(handler):
                handler(session)

    # ------------------------------------------------------------------
    # Student: Request a session
    # ------------------------------------------------------------------

    def request_session(
        self,
        mentor_id: UUID,
        mentee_id: UUID,
        subject_id: int,
        scheduled_at: datetime,
        end_at: datetime,
        notes: Optional[str] = None,
    ) -> SessionModel:
        """
        Student requests a session with a mentor.
        Validates availability, creates session with 'pending' status,
        notifies mentor via observers.
        """
        mentor: Optional[User] = self._db.query(User).filter(User.id == mentor_id).first()
        if not mentor or not mentor.is_mentor:
            raise ValueError(f"User {mentor_id} is not a valid mentor.")

        self._check_not_unavailable(mentor_id, scheduled_at, end_at)
        self._check_no_overlap(mentor_id, scheduled_at, end_at)

        duration_minutes = int((end_at - scheduled_at).total_seconds() / 60)
        if duration_minutes <= 0:
            raise ValueError("Session end time must be after start time.")

        session = SessionModel(
            mentor_id=mentor_id,
            mentee_id=mentee_id,
            subject_id=subject_id,
            scheduled_at=scheduled_at,
            end_at=end_at,
            duration_minutes=duration_minutes,
            status="pending",
            notes=notes,
        )
        self._repo.create(session)
        self._db.commit()
        self._db.refresh(session)

        self._notify("on_session_requested", session)
        return session

    # ------------------------------------------------------------------
    # Mentor: Confirm / Decline
    # ------------------------------------------------------------------

    def confirm_session(self, session_id: UUID, mentor_id: UUID) -> SessionModel:
        """Mentor confirms a pending session. Transitions: pending → confirmed."""
        session = self._get_and_authorize(session_id, mentor_id, role="mentor")
        sm = SessionStateMachine(session.status)
        session.status = sm.transition("confirmed")
        self._db.commit()
        self._db.refresh(session)
        self._notify("on_session_confirmed", session)
        return session

    def decline_session(self, session_id: UUID, mentor_id: UUID) -> SessionModel:
        """Mentor declines a pending session. Transitions: pending → declined."""
        session = self._get_and_authorize(session_id, mentor_id, role="mentor")
        sm = SessionStateMachine(session.status)
        session.status = sm.transition("declined")
        self._db.commit()
        self._db.refresh(session)
        self._notify("on_session_declined", session)
        return session

    # ------------------------------------------------------------------
    # Either party: Cancel
    # ------------------------------------------------------------------

    def cancel_session(self, session_id: UUID, user_id: UUID) -> SessionModel:
        """Either mentor or mentee can cancel a pending or confirmed session."""
        session = self._repo.get_by_id(session_id)
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found.")
        if session.mentor_id != user_id and session.mentee_id != user_id:
            raise UnauthorizedSessionActionException("You are not part of this session.")

        sm = SessionStateMachine(session.status)
        session.status = sm.transition("cancelled")
        self._db.commit()
        self._db.refresh(session)
        self._notify("on_session_cancelled", session)
        return session

    # ------------------------------------------------------------------
    # APScheduler: Complete
    # ------------------------------------------------------------------

    def complete_session(self, session_id: UUID) -> SessionModel:
        """
        Mark session as completed (called by APScheduler after end_at).
        Transitions: confirmed → completed.
        """
        session = self._repo.get_by_id(session_id)
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found.")

        sm = SessionStateMachine(session.status)
        session.status = sm.transition("completed")
        self._db.commit()
        self._db.refresh(session)
        self._notify("on_session_completed", session)
        return session

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_pending_requests(self, mentor_id: UUID) -> List[SessionModel]:
        """Typed generics: List[Session]."""
        return self._repo.get_pending_requests_for_mentor(mentor_id)

    def get_mentor_calendar(self, mentor_id: UUID) -> List[Dict[str, Any]]:
        """Upcoming confirmed sessions for mentor's calendar. Uses list comprehension."""
        sessions = self._repo.get_mentor_sessions(mentor_id, status="confirmed")
        return [
            {
                "id": str(s.id),
                "subject_id": s.subject_id,
                "mentee_id": str(s.mentee_id),
                "scheduled_at": s.scheduled_at.isoformat(),
                "end_at": s.end_at.isoformat(),
                "duration_minutes": s.duration_minutes,
                "status": s.status,
                "notes": s.notes,
            }
            for s in sessions
        ]

    def get_student_calendar(self, mentee_id: UUID) -> List[Dict[str, Any]]:
        """Upcoming confirmed sessions for student's calendar."""
        sessions = self._repo.get_mentee_sessions(mentee_id, status="confirmed")
        return [
            {
                "id": str(s.id),
                "subject_id": s.subject_id,
                "subject_name": s.subject.name if s.subject else "",
                "mentor_id": str(s.mentor_id),
                "mentor_name": f"{s.mentor.first_name} {s.mentor.last_name}" if s.mentor else "",
                "scheduled_at": s.scheduled_at.isoformat(),
                "end_at": s.end_at.isoformat(),
                "duration_minutes": s.duration_minutes,
                "status": s.status,
            }
            for s in sessions
        ]

    def get_student_history(self, mentee_id: UUID) -> List[Dict[str, Any]]:
        """
        Completed sessions for student history.
        Uses filter() and map() — curriculum requirement.
        """
        sessions = self._repo.get_mentee_sessions(mentee_id, status="completed")

        reviewed_ids = set(
            filter(None, map(lambda s: str(s.id) if s.review else None, sessions))
        )

        return [
            {
                "id": str(s.id),
                "subject_id": s.subject_id,
                "subject_name": s.subject.name if s.subject else "",
                "mentor_id": str(s.mentor_id),
                "mentor_name": f"{s.mentor.first_name} {s.mentor.last_name}" if s.mentor else "",
                "scheduled_at": s.scheduled_at.isoformat(),
                "duration_minutes": s.duration_minutes,
                "has_review": str(s.id) in reviewed_ids,
            }
            for s in sessions
        ]

    # ------------------------------------------------------------------
    # Availability management
    # ------------------------------------------------------------------

    def set_availability(
        self, mentor_id: UUID, day_of_week: int, start_time, end_time,
        is_recurring: bool = True,
    ) -> Availability:
        avail = Availability(
            mentor_id=mentor_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            is_recurring=is_recurring,
        )
        self._repo.add_availability(avail)
        self._db.commit()
        self._db.refresh(avail)
        return avail

    def get_availability(self, mentor_id: UUID) -> List[Availability]:
        return self._repo.get_availabilities(mentor_id)

    def remove_availability(self, avail_id: UUID, mentor_id: UUID) -> None:
        avails = self._repo.get_availabilities(mentor_id)
        owned = list(filter(lambda a: a.id == avail_id, avails))
        if not owned:
            raise UnauthorizedSessionActionException(
                "Availability slot not found or not owned by this mentor."
            )
        self._repo.delete_availability(avail_id)
        self._db.commit()

    # ------------------------------------------------------------------
    # Unavailable slots
    # ------------------------------------------------------------------

    def add_unavailable_slot(
        self, mentor_id: UUID, start_datetime: datetime,
        end_datetime: datetime, reason: Optional[str] = None,
    ) -> UnavailableSlot:
        slot = UnavailableSlot(
            mentor_id=mentor_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            reason=reason,
        )
        self._repo.add_unavailable_slot(slot)
        self._db.commit()
        self._db.refresh(slot)
        return slot

    def get_unavailable_slots(self, mentor_id: UUID) -> List[Dict[str, Any]]:
        slots = self._repo.get_unavailable_slots(mentor_id)
        return [
            {
                "id": str(s.id),
                "start_datetime": s.start_datetime.isoformat(),
                "end_datetime": s.end_datetime.isoformat(),
                "reason": s.reason,
            }
            for s in slots
        ]

    def remove_unavailable_slot(self, slot_id: UUID, mentor_id: UUID) -> bool:
        result = self._repo.delete_unavailable_slot(slot_id, mentor_id)
        if result:
            self._db.commit()
        return result

    # ------------------------------------------------------------------
    # Strategy Pattern entry point: find and rank mentors
    # ------------------------------------------------------------------

    def find_mentors(
        self,
        subject_id: Optional[int] = None,
        name: Optional[str] = None,
        student_grade: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Find and rank mentors using the Strategy Pattern."""
        from app.auth.repository import UserRepository

        user_repo = UserRepository(self._db)
        all_mentors = user_repo.search_mentors(name=name, subject_id=subject_id)
        mentor_ids = [m.id for m in all_mentors]

        avg_ratings: Dict[UUID, float] = {
            m.id: user_repo.get_average_rating(m.id) for m in all_mentors
        }

        mentor_subject_map: Dict[UUID, List[int]] = {}
        ms_rows = (
            self._db.query(MentorSubject)
            .filter(MentorSubject.mentor_id.in_(mentor_ids))
            .all()
        )
        for ms in ms_rows:
            mentor_subject_map.setdefault(ms.mentor_id, []).append(ms.subject_id)

        all_subject_ids = {sid for ids in mentor_subject_map.values() for sid in ids}
        subject_name_map: Dict[int, str] = {}
        if all_subject_ids:
            for s in self._db.query(Subject).filter(Subject.id.in_(all_subject_ids)).all():
                subject_name_map[s.id] = s.name

        context = {
            "subject_id": subject_id,
            "avg_ratings": avg_ratings,
            "mentor_subject_map": mentor_subject_map,
            "student_grade": student_grade or 8,
        }

        matcher = build_matcher(subject_id=subject_id)
        ranked = matcher.match(all_mentors, context)

        return [
            {
                "id": str(m.id),
                "first_name": m.first_name,
                "last_name": m.last_name,
                "grade": m.grade,
                "class_letter": m.class_letter,
                "average_rating": avg_ratings.get(m.id, 0.0),
                "subjects": [
                    {"id": sid, "name": subject_name_map.get(sid, "")}
                    for sid in mentor_subject_map.get(m.id, [])
                ],
            }
            for m in ranked
        ]

    # ------------------------------------------------------------------
    # Private helpers (Encapsulation)
    # ------------------------------------------------------------------

    def _check_not_unavailable(self, mentor_id: UUID, start: datetime, end: datetime) -> None:
        """Raise MentorUnavailableException if time overlaps with unavailable slot."""
        overlapping = self._repo.get_overlapping_unavailable_slots(mentor_id, start, end)
        if overlapping:
            raise MentorUnavailableException(
                "The mentor is unavailable at the selected time."
            )

    def _check_no_overlap(self, mentor_id: UUID, start: datetime, end: datetime) -> None:
        """Raise SessionConflictException if mentor already has a session in this window."""
        conflicts = self._repo.get_sessions_between(mentor_id, start, end)
        if conflicts:
            raise SessionConflictException(
                "The mentor already has a session during this time."
            )

    def _get_and_authorize(self, session_id: UUID, user_id: UUID, role: str) -> SessionModel:
        """Fetch session and verify the caller is the correct participant."""
        session = self._repo.get_by_id(session_id)
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found.")
        if role == "mentor" and session.mentor_id != user_id:
            raise UnauthorizedSessionActionException(
                "Only the mentor of this session can perform this action."
            )
        if role == "mentee" and session.mentee_id != user_id:
            raise UnauthorizedSessionActionException(
                "Only the student of this session can perform this action."
            )
        return session
