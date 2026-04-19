"""
db/models/availability.py — Availability and UnavailableSlot models.

Availability: recurring weekly time slots when a mentor is free.
UnavailableSlot: specific date-time ranges a mentor marks as blocked.
"""

import uuid

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.models.base import Base


class Availability(Base):
    """
    Recurring weekly availability slot for a mentor.
    day_of_week: 0=Monday … 6=Sunday
    """
    __tablename__ = "availabilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    day_of_week = Column(
        Integer,
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6"),
        nullable=False,
    )
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_recurring = Column(Boolean, default=True, nullable=False)

    mentor = relationship("User", back_populates="availabilities")

    def __repr__(self) -> str:
        return f"<Availability mentor={self.mentor_id} day={self.day_of_week}>"


class UnavailableSlot(Base):
    """
    A specific date-time range a mentor marks as unavailable.
    Students cannot book sessions during these periods.
    If a student tries, the frontend shows: 'The mentor is unavailable at the selected time.'
    """
    __tablename__ = "unavailable_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=True)

    mentor = relationship("User", back_populates="unavailable_slots")

    def __repr__(self) -> str:
        return f"<UnavailableSlot mentor={self.mentor_id} {self.start_datetime}>"
