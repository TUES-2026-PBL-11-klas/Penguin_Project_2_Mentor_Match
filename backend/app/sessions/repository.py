from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session as DBSession

from app.db.models.availability import Availability, UnavailableSlot
from app.db.models.session import Session as SessionModel


class SessionRepository:
    """Data access layer — only DB queries, zero business logic."""

    def __init__(self, db: DBSession) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def create(self, session: SessionModel) -> SessionModel:
        self._db.add(session)
        self._db.flush()
        return session

    def get_by_id(self, session_id: UUID) -> Optional[SessionModel]:
        return self._db.query(SessionModel).filter(SessionModel.id == session_id).first()

    def get_mentor_sessions(
        self, mentor_id: UUID, status: Optional[str] = None
    ) -> List[SessionModel]:
        q = self._db.query(SessionModel).filter(SessionModel.mentor_id == mentor_id)
        if status:
            q = q.filter(SessionModel.status == status)
        return q.order_by(SessionModel.scheduled_at.asc()).all()

    def get_mentee_sessions(
        self, mentee_id: UUID, status: Optional[str] = None
    ) -> List[SessionModel]:
        q = self._db.query(SessionModel).filter(SessionModel.mentee_id == mentee_id)
        if status:
            q = q.filter(SessionModel.status == status)
        return q.order_by(SessionModel.scheduled_at.asc()).all()

    def get_pending_requests_for_mentor(self, mentor_id: UUID) -> List[SessionModel]:
        """All pending session requests for a mentor."""
        return (
            self._db.query(SessionModel)
            .filter(
                SessionModel.mentor_id == mentor_id,
                SessionModel.status == "pending",
            )
            .order_by(SessionModel.created_at.asc())
            .all()
        )

    def get_sessions_between(
        self, mentor_id: UUID, start: datetime, end: datetime
    ) -> List[SessionModel]:
        """Find pending/confirmed sessions overlapping with a time window."""
        return (
            self._db.query(SessionModel)
            .filter(
                SessionModel.mentor_id == mentor_id,
                SessionModel.status.in_(["pending", "confirmed"]),
                SessionModel.scheduled_at < end,
                SessionModel.end_at > start,
            )
            .all()
        )

    # ------------------------------------------------------------------
    # Availability (recurring weekly slots)
    # ------------------------------------------------------------------

    def get_availabilities(self, mentor_id: UUID) -> List[Availability]:
        return (
            self._db.query(Availability)
            .filter(Availability.mentor_id == mentor_id)
            .all()
        )

    def add_availability(self, avail: Availability) -> Availability:
        self._db.add(avail)
        self._db.flush()
        return avail

    def delete_availability(self, avail_id: UUID) -> None:
        avail = self._db.query(Availability).filter(Availability.id == avail_id).first()
        if avail:
            self._db.delete(avail)
            self._db.flush()

    # ------------------------------------------------------------------
    # Unavailable Slots
    # ------------------------------------------------------------------

    def get_unavailable_slots(self, mentor_id: UUID) -> List[UnavailableSlot]:
        return (
            self._db.query(UnavailableSlot)
            .filter(UnavailableSlot.mentor_id == mentor_id)
            .order_by(UnavailableSlot.start_datetime.asc())
            .all()
        )

    def add_unavailable_slot(self, slot: UnavailableSlot) -> UnavailableSlot:
        self._db.add(slot)
        self._db.flush()
        return slot

    def delete_unavailable_slot(self, slot_id: UUID, mentor_id: UUID) -> bool:
        slot = (
            self._db.query(UnavailableSlot)
            .filter(
                UnavailableSlot.id == slot_id,
                UnavailableSlot.mentor_id == mentor_id,
            )
            .first()
        )
        if slot:
            self._db.delete(slot)
            self._db.flush()
            return True
        return False

    def get_overlapping_unavailable_slots(
        self, mentor_id: UUID, start: datetime, end: datetime
    ) -> List[UnavailableSlot]:
        """Find unavailable slots overlapping with a proposed session window."""
        return (
            self._db.query(UnavailableSlot)
            .filter(
                UnavailableSlot.mentor_id == mentor_id,
                UnavailableSlot.start_datetime < end,
                UnavailableSlot.end_datetime > start,
            )
            .all()
        )