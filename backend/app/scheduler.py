"""
scheduler.py — APScheduler jobs for background tasks.

Jobs:
  send_24h_reminders  runs every hour; finds confirmed sessions starting in
                      23-25 h and sends a session_reminder notification to
                      both the mentor and the mentee (idempotent: skips if a
                      reminder has already been sent for that user+session).
"""

import logging
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import and_, select

from app.db.models.notification import Notification
from app.db.models.session import Session as SessionModel
from app.db.models.subject import Subject
from app.db.session import SessionLocal
from app.notifications.service import WebPushNotificationService

logger = logging.getLogger(__name__)


def _notification_service() -> WebPushNotificationService:
    return WebPushNotificationService(
        vapid_private_key=os.getenv("VAPID_PRIVATE_KEY", "dummy_private_key"),
        vapid_claims={
            "sub": f"mailto:{os.getenv('VAPID_ADMIN_EMAIL', 'admin@mentormatch.local')}"
        },
    )


def send_24h_reminders() -> None:
    """Send session_reminder notifications for sessions starting in ~24 hours."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        window_start = now + timedelta(hours=23)
        window_end = now + timedelta(hours=25)

        upcoming = db.scalars(
            select(SessionModel).where(
                and_(
                    SessionModel.status == "confirmed",
                    SessionModel.scheduled_at >= window_start,
                    SessionModel.scheduled_at <= window_end,
                )
            )
        ).all()

        if not upcoming:
            return

        svc = _notification_service()

        for session in upcoming:
            subject = db.scalars(
                select(Subject).where(Subject.id == session.subject_id)
            ).first()
            subject_name = subject.name if subject else "session"
            time_str = session.scheduled_at.strftime("%H:%M on %d %b")
            message = f"Reminder: your {subject_name} session is at {time_str}."

            for user_id in (session.mentor_id, session.mentee_id):
                already_sent = db.scalars(
                    select(Notification).where(
                        and_(
                            Notification.session_id == session.id,
                            Notification.type == "session_reminder",
                            Notification.user_id == user_id,
                        )
                    )
                ).first()

                if already_sent:
                    continue

                try:
                    svc.send_notification(
                        db=db,
                        user_id=user_id,
                        title="Session Reminder",
                        message=message,
                        type="session_reminder",
                        session_id=session.id,
                    )
                    logger.info(
                        "Sent 24h reminder to user %s for session %s",
                        user_id,
                        session.id,
                    )
                except Exception as exc:
                    logger.error(
                        "Failed to send reminder to %s for session %s: %s",
                        user_id,
                        session.id,
                        exc,
                    )

    except Exception as exc:
        logger.error("send_24h_reminders job failed: %s", exc)
    finally:
        SessionLocal.remove()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        send_24h_reminders,
        trigger="interval",
        hours=1,
        id="send_24h_reminders",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started — 24h reminder job registered.")
    return scheduler
