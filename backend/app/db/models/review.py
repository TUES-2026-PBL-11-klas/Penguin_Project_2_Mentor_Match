import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

class Review(Base):
    """
    Review left by a student after a completed session.
    rating: 0–5 stars (as specified in Mentor_Match_Logic).
    One review per session (unique constraint on session_id).
    """
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False, unique=True
    )
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reviewed_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    rating = Column(
        Integer,
        CheckConstraint("rating >= 0 AND rating <= 5"),
        nullable=False,
    )
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="review")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewed_user = relationship(
        "User", foreign_keys=[reviewed_user_id], back_populates="reviews_received"
    )

    def __repr__(self) -> str:
        return f"<Review session={self.session_id} rating={self.rating}>"
