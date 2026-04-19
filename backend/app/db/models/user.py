"""
db/models/user.py — User model.
A user can be a student, mentor, or both.
"""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.models.base import Base


class User(Base):
    """
    Central user table. A user can be a student, mentor, or both.
    OOP: encapsulates all identity + role data.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # School-specific fields (from Mentor_Match_Logic)
    grade = Column(
        Integer,
        CheckConstraint("grade >= 8 AND grade <= 12"),
        nullable=False,
    )
    class_letter = Column(
        String(1),
        CheckConstraint("class_letter IN ('A','B','C','D','E','F','G')"),
        nullable=False,
    )

    # Role: student | mentor | both
    role = Column(
        Enum("student", "mentor", "both", name="user_role_enum"),
        nullable=False,
        default="student",
    )

    profile_picture = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships (string references avoid circular imports)
    mentor_subjects = relationship(
        "MentorSubject", back_populates="mentor", cascade="all, delete-orphan"
    )
    availabilities = relationship(
        "Availability", back_populates="mentor", cascade="all, delete-orphan"
    )
    unavailable_slots = relationship(
        "UnavailableSlot", back_populates="mentor", cascade="all, delete-orphan"
    )
    sessions_as_mentor = relationship(
        "Session",
        foreign_keys="Session.mentor_id",
        back_populates="mentor",
    )
    sessions_as_mentee = relationship(
        "Session",
        foreign_keys="Session.mentee_id",
        back_populates="mentee",
    )
    reviews_given = relationship(
        "Review", foreign_keys="Review.reviewer_id", back_populates="reviewer"
    )

    reviews_received = relationship(
        "Review", foreign_keys="Review.reviewed_user_id", back_populates="reviewed_user"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def is_mentor(self) -> bool:
        """Encapsulation: hide role string comparison behind a clean property."""
        return self.role in ("mentor", "both")

    @property
    def is_student(self) -> bool:
        return self.role in ("student", "both")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"
