import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

class Notification(Base):
    """
    In-app notification for a user.

    Types:
      - new_request:        mentor receives when a student books a session
      - session_confirmed:  student receives when mentor accepts
      - session_declined:   student receives when mentor declines
      - session_reminder:   sent the day before the session starts
      - rate_session:       sent to student 10 minutes after session ends
    """
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True)

    type = Column(
        Enum(
            "new_request",
            "session_confirmed",
            "session_declined",
            "session_reminder",
            "rate_session",
            name="notification_type_enum",
        ),
        nullable=False,
    )
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)  # when to send (for scheduled notifications)
    sent_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="notifications")
    session = relationship("Session", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification user={self.user_id} type={self.type} read={self.is_read}>"
