import os
from datetime import datetime
from uuid import UUID

from flask import Blueprint, g, jsonify, request

from app.auth.middleware import require_auth, require_mentor
from app.db.models.user import User
from app.db.session import get_db
from app.notifications.service import WebPushNotificationService
from app.sessions.exceptions import (
    MentorUnavailableException,
    SessionConflictException,
    SessionNotFoundException,
    UnauthorizedSessionActionException,
)
from app.sessions.service import SessionEventObserver, SessionService

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")

_notif_svc = WebPushNotificationService(
    vapid_private_key=os.getenv("VAPID_PRIVATE_KEY", "dummy_private_key"),
    vapid_claims={"sub": f"mailto:{os.getenv('VAPID_ADMIN_EMAIL', 'admin@mentormatch.local')}"},
)


class _NotificationObserver(SessionEventObserver):
    def __init__(self, db):
        self._db = db

    def _send(self, user_id, title, message, ntype, session_id):
        try:
            _notif_svc.send_notification(
                db=self._db, user_id=user_id,
                title=title, message=message,
                type=ntype, session_id=session_id,
            )
        except Exception:
            pass

    def on_session_requested(self, session):
        self._send(session.mentor_id, "New Session Request",
                   "A student has requested a session with you.",
                   "new_request", session.id)

    def on_session_confirmed(self, session):
        self._send(session.mentee_id, "Session Confirmed",
                   "Your session request has been confirmed!",
                   "session_confirmed", session.id)

    def on_session_declined(self, session):
        self._send(session.mentee_id, "Session Declined",
                   "Your session request has been declined.",
                   "session_declined", session.id)

    def on_session_completed(self, session):
        self._send(session.mentee_id, "Rate Your Session",
                   "Your session is complete — leave a review for your mentor!",
                   "rate_session", session.id)


def _make_svc(db) -> SessionService:
    svc = SessionService(db)
    svc.register_observer(_NotificationObserver(db))
    return svc


# ------------------------------------------------------------------
# Student: Request a session
# ------------------------------------------------------------------

@sessions_bp.route("/request", methods=["POST"])
@require_auth
def request_session():
    """POST /api/sessions/request"""
    data = request.get_json() or {}
    required = ["mentor_id", "subject_id", "scheduled_at", "end_at"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        scheduled_at = datetime.fromisoformat(data["scheduled_at"])
        end_at = datetime.fromisoformat(data["end_at"])
        mentor_id = UUID(data["mentor_id"])
        subject_id = int(data["subject_id"])
    except (ValueError, KeyError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400

    with get_db() as db:
        svc = _make_svc(db)
        try:
            session = svc.request_session(
                mentor_id=mentor_id,
                mentee_id=g.current_user_id,
                subject_id=subject_id,
                scheduled_at=scheduled_at,
                end_at=end_at,
                notes=data.get("notes"),
            )
            return jsonify({"session_id": str(session.id), "status": session.status}), 201
        except MentorUnavailableException as e:
            return jsonify({"error": str(e)}), 409
        except SessionConflictException as e:
            return jsonify({"error": str(e)}), 409
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


# ------------------------------------------------------------------
# Mentor: View pending requests
# ------------------------------------------------------------------

@sessions_bp.route("/requests", methods=["GET"])
@require_mentor
def get_pending_requests():
    """GET /api/sessions/requests — mentor's session requests page."""
    with get_db() as db:
        svc = SessionService(db)
        sessions = svc.get_pending_requests(g.current_user_id)
        result = [
            {
                "id": str(s.id),
                "mentee_id": str(s.mentee_id),
                "subject_id": s.subject_id,
                "scheduled_at": s.scheduled_at.isoformat(),
                "end_at": s.end_at.isoformat(),
                "duration_minutes": s.duration_minutes,
                "notes": s.notes,
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]
        return jsonify(result), 200


# ------------------------------------------------------------------
# Mentor: Confirm or decline
# ------------------------------------------------------------------

@sessions_bp.route("/<session_id>/confirm", methods=["POST"])
@require_mentor
def confirm_session(session_id: str):
    """POST /api/sessions/<id>/confirm"""
    with get_db() as db:
        svc = _make_svc(db)
        try:
            session = svc.confirm_session(UUID(session_id), g.current_user_id)
            return jsonify({"status": session.status}), 200
        except (SessionNotFoundException, UnauthorizedSessionActionException) as e:
            return jsonify({"error": str(e)}), 400


@sessions_bp.route("/<session_id>/decline", methods=["POST"])
@require_mentor
def decline_session(session_id: str):
    """POST /api/sessions/<id>/decline"""
    with get_db() as db:
        svc = _make_svc(db)
        try:
            session = svc.decline_session(UUID(session_id), g.current_user_id)
            return jsonify({"status": session.status}), 200
        except (SessionNotFoundException, UnauthorizedSessionActionException) as e:
            return jsonify({"error": str(e)}), 400


# ------------------------------------------------------------------
# Either party: Cancel
# ------------------------------------------------------------------

@sessions_bp.route("/<session_id>/cancel", methods=["POST"])
@require_auth
def cancel_session(session_id: str):
    """POST /api/sessions/<id>/cancel"""
    with get_db() as db:
        svc = _make_svc(db)
        try:
            session = svc.cancel_session(UUID(session_id), g.current_user_id)
            return jsonify({"status": session.status}), 200
        except (SessionNotFoundException, UnauthorizedSessionActionException) as e:
            return jsonify({"error": str(e)}), 400


# ------------------------------------------------------------------
# Calendars
# ------------------------------------------------------------------

@sessions_bp.route("/mentor/calendar", methods=["GET"])
@require_mentor
def mentor_calendar():
    """GET /api/sessions/mentor/calendar"""
    with get_db() as db:
        svc = SessionService(db)
        return jsonify(svc.get_mentor_calendar(g.current_user_id)), 200


@sessions_bp.route("/student/calendar", methods=["GET"])
@require_auth
def student_calendar():
    """GET /api/sessions/student/calendar"""
    with get_db() as db:
        svc = SessionService(db)
        return jsonify(svc.get_student_calendar(g.current_user_id)), 200


@sessions_bp.route("/student/history", methods=["GET"])
@require_auth
def student_history():
    """GET /api/sessions/student/history"""
    with get_db() as db:
        svc = SessionService(db)
        return jsonify(svc.get_student_history(g.current_user_id)), 200


# ------------------------------------------------------------------
# Mentor: Availability (recurring weekly schedule)
# ------------------------------------------------------------------

@sessions_bp.route("/availability", methods=["GET"])
@require_mentor
def get_availability():
    with get_db() as db:
        svc = SessionService(db)
        avails = svc.get_availability(g.current_user_id)
        return jsonify([
            {
                "id": str(a.id),
                "day_of_week": a.day_of_week,
                "start_time": a.start_time.isoformat(),
                "end_time": a.end_time.isoformat(),
                "is_recurring": a.is_recurring,
            }
            for a in avails
        ]), 200


@sessions_bp.route("/availability", methods=["POST"])
@require_mentor
def add_availability():
    data = request.get_json() or {}
    try:
        from datetime import time
        start_time = time.fromisoformat(data["start_time"])
        end_time = time.fromisoformat(data["end_time"])
        day_of_week = int(data["day_of_week"])
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400

    with get_db() as db:
        svc = SessionService(db)
        avail = svc.set_availability(
            mentor_id=g.current_user_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            is_recurring=data.get("is_recurring", True),
        )
        return jsonify({"id": str(avail.id)}), 201


@sessions_bp.route("/availability/<avail_id>", methods=["DELETE"])
@require_mentor
def delete_availability(avail_id: str):
    with get_db() as db:
        svc = SessionService(db)
        try:
            svc.remove_availability(UUID(avail_id), g.current_user_id)
            return jsonify({"message": "Removed"}), 200
        except UnauthorizedSessionActionException as e:
            return jsonify({"error": str(e)}), 403


# ------------------------------------------------------------------
# Unavailable slots
# ------------------------------------------------------------------

@sessions_bp.route("/unavailable", methods=["GET"])
@require_auth
def get_unavailable():
    """GET /api/sessions/unavailable?mentor_id=<id>"""
    mentor_id_str = request.args.get("mentor_id")
    if not mentor_id_str:
        mentor_id = g.current_user_id
    else:
        try:
            mentor_id = UUID(mentor_id_str)
        except ValueError:
            return jsonify({"error": "Invalid mentor_id"}), 400

    with get_db() as db:
        svc = SessionService(db)
        return jsonify(svc.get_unavailable_slots(mentor_id)), 200


@sessions_bp.route("/unavailable", methods=["POST"])
@require_mentor
def add_unavailable():
    data = request.get_json() or {}
    try:
        start = datetime.fromisoformat(data["start_datetime"])
        end = datetime.fromisoformat(data["end_datetime"])
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400

    with get_db() as db:
        svc = SessionService(db)
        slot = svc.add_unavailable_slot(
            mentor_id=g.current_user_id,
            start_datetime=start,
            end_datetime=end,
            reason=data.get("reason"),
        )
        return jsonify({"id": str(slot.id)}), 201


@sessions_bp.route("/unavailable/<slot_id>", methods=["DELETE"])
@require_mentor
def delete_unavailable(slot_id: str):
    with get_db() as db:
        svc = SessionService(db)
        removed = svc.remove_unavailable_slot(UUID(slot_id), g.current_user_id)
        if removed:
            return jsonify({"message": "Removed"}), 200
        return jsonify({"error": "Slot not found"}), 404


# ------------------------------------------------------------------
# Mentor search (Strategy Pattern entry point)
# ------------------------------------------------------------------

@sessions_bp.route("/mentors/search", methods=["GET"])
@require_auth
def search_mentors():
    """GET /api/sessions/mentors/search?subject_id=&name="""
    subject_id = request.args.get("subject_id", type=int)
    name = request.args.get("name")

    with get_db() as db:
        svc = SessionService(db)
        student = db.query(User).filter(User.id == g.current_user_id).first()
        student_grade = student.grade if student else None
        mentors = svc.find_mentors(
            subject_id=subject_id,
            name=name,
            student_grade=student_grade,
        )
        return jsonify(mentors), 200
