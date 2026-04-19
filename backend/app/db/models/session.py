import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

class Session(Base):
    """
    A booked mentoring session between a mentor and a student.
    Status transitions are enforced by sessions/state_machine.py.
    """
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    mentee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    scheduled_at = Column(DateTime, nullable=False)   # session start datetime
    end_at = Column(DateTime, nullable=False)          # session end datetime
    duration_minutes = Column(Integer, nullable=False)

    status = Column(
        Enum(
            "pending",
            "confirmed",
            "completed",
            "declined",
            "cancelled",
            name="session_status_enum",
        ),
        nullable=False,
        default="pending",
    )

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    mentor = relationship("User", foreign_keys=[mentor_id], back_populates="sessions_as_mentor")
    mentee = relationship("User", foreign_keys=[mentee_id], back_populates="sessions_as_mentee")
    subject = relationship("Subject", back_populates="sessions")
    review = relationship("Review", back_populates="session", uselist=False)
    notifications = relationship("Notification", back_populates="session")

    def __repr__(self) -> str:
        return f"<Session {self.id} status={self.status}>"
