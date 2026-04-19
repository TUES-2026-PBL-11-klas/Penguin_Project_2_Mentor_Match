"""
db/models/subject.py — Subject and MentorSubject models.
Subject: lookup table of school subjects.
MentorSubject: N:N join between mentors and subjects.
"""

import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.models.base import Base


class Subject(Base):
    """Lookup table for school subjects (e.g. Mathematics, Biology)."""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=True)  # e.g. "Science", "Humanities"

    mentor_subjects = relationship("MentorSubject", back_populates="subject")
    sessions = relationship("Session", back_populates="subject")

    def __repr__(self) -> str:
        return f"<Subject {self.name}>"


class MentorSubject(Base):
    """N:N join table — which mentor teaches which subject."""
    __tablename__ = "mentor_subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade_level = Column(Integer, nullable=True)  # highest grade the mentor can help with

    mentor = relationship("User", back_populates="mentor_subjects")
    subject = relationship("Subject", back_populates="mentor_subjects")

    def __repr__(self) -> str:
        return f"<MentorSubject mentor={self.mentor_id} subject={self.subject_id}>"
