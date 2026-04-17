from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.mentor_profile import MentorProfile
    from app.db.models.notification import Notification
    from app.db.models.review import Review
    from app.db.models.subject import Subject
    from app.db.models.user import User

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
    mentor_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("mentor_profiles.id", ondelete="CASCADE")
    )
    mentee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(session_status_enum, nullable=False, server_default="pending")
    meeting_link: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    mentor: Mapped["User"] = relationship(
        "User", back_populates="mentor_sessions", foreign_keys=[mentor_id]
    )
    student: Mapped["User"] = relationship(
        "User", back_populates="student_sessions", foreign_keys=[student_id]
    )
    mentor_profile: Mapped["MentorProfile | None"] = relationship(
        "MentorProfile",
        back_populates="sessions",
        foreign_keys=[mentor_profile_id],
    )
    subject: Mapped["Subject"] = relationship("Subject", back_populates="sessions")
    review: Mapped["Review | None"] = relationship(
        "Review", back_populates="session", uselist=False
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="session",
        cascade="all, delete-orphan",
    )
