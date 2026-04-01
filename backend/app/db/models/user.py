from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.common import TimestampMixin

user_role_enum = Enum("mentor", "student", name="user_role")


mentor_subjects = Table(
    "mentor_subjects",
    Base.metadata,
    Column("mentor_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
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
    grade_level: Mapped[int | None] = mapped_column(Integer)
    bio: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    subjects = relationship(
        "Subject",
        secondary=mentor_subjects,
        back_populates="mentors",
    )
    mentor_availabilities = relationship(
        "Availability",
        back_populates="mentor",
        cascade="all, delete-orphan",
        foreign_keys="Availability.mentor_id",
    )
    mentor_sessions = relationship(
        "Session",
        back_populates="mentor",
        foreign_keys="Session.mentor_id",
    )
    student_sessions = relationship(
        "Session",
        back_populates="student",
        foreign_keys="Session.student_id",
    )
    reviews_written = relationship(
        "Review",
        back_populates="student",
        foreign_keys="Review.student_id",
    )
    reviews_received = relationship(
        "Review",
        back_populates="mentor",
        foreign_keys="Review.mentor_id",
    )
