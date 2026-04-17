from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.availability import Availability
    from app.db.models.mentor_profile import MentorProfile
    from app.db.models.notification import Notification
    from app.db.models.review import Review
    from app.db.models.session import Session
    from app.db.models.subject import Subject

user_role_enum = Enum("mentor", "student", name="user_role")


mentor_subjects = Table(
    "mentor_subjects",
    Base.metadata,
    Column("mentor_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
    Column("grade_level", Integer, nullable=True),
    UniqueConstraint("mentor_id", "subject_id", name="uq_mentor_subject"),
)


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(user_role_enum, nullable=False)
    profile_picture: Mapped[str | None] = mapped_column(String(255))
    grade_level: Mapped[int | None] = mapped_column(Integer)
    bio: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    subjects: Mapped[list["Subject"]] = relationship(
        "Subject",
        secondary=mentor_subjects,
        back_populates="mentors",
        overlaps="mentor_links,subject",
    )
    mentor_availabilities: Mapped[list["Availability"]] = relationship(
        "Availability",
        back_populates="mentor",
        cascade="all, delete-orphan",
        foreign_keys="Availability.mentor_id",
    )
    mentor_sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="mentor",
        foreign_keys="Session.mentor_id",
    )
    student_sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="student",
        foreign_keys="Session.student_id",
    )
    reviews_written: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="student",
        foreign_keys="Review.student_id",
    )
    reviews_received: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="mentor",
        foreign_keys="Review.mentor_id",
    )
    mentor_profile: Mapped["MentorProfile | None"] = relationship(
        "MentorProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
