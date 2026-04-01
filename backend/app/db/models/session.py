from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.common import TimestampMixin

session_status_enum = Enum(
    "pending",
    "confirmed",
    "completed",
    "cancelled",
    name="session_status",
)


class Session(TimestampMixin, Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    mentor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(session_status_enum, nullable=False, server_default="pending")
    meeting_link: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    mentor = relationship("User", back_populates="mentor_sessions", foreign_keys=[mentor_id])
    student = relationship("User", back_populates="student_sessions", foreign_keys=[student_id])
    subject = relationship("Subject")
    review = relationship("Review", back_populates="session", uselist=False)
