from abc import ABC, abstractmethod
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.review import Review
from app.db.models.session import Session as DbSession
from app.common.exceptions import ReviewAlreadyExistsException, SessionNotCompletedException
from app.common.utils import db_transaction_manager


class IReviewService(ABC):
    """Abstract Base Class for ReviewService (SOLID - Dependency Inversion)"""

    @abstractmethod
    def create_review(self, db: Session, session_id: UUID, student_id: UUID, rating: int, comment: str | None = None) -> Review:
        pass

    @abstractmethod
    def get_mentor_reviews(self, db: Session, mentor_id: UUID) -> Dict[str, Any]:
        pass


class ReviewService(IReviewService):

    def create_review(self, db: Session, session_id: UUID, student_id: UUID, rating: int, comment: str | None = None) -> Review:
        # Fetch session
        db_session = db.scalars(select(DbSession).where(DbSession.id == session_id)).first()
        if not db_session:
            raise ValueError("Session not found")

        # Must be the mentee
        if db_session.mentee_id != student_id:
            raise ValueError("Unauthorized: you are not the student of this session")

        # Session must be completed
        if db_session.status != "completed":
            raise SessionNotCompletedException()

        # One review per session
        existing_review = db.scalars(select(Review).where(Review.session_id == session_id)).first()
        if existing_review:
            raise ReviewAlreadyExistsException()

        # Validate rating
        if not (0 <= rating <= 5):
            raise ValueError("Rating must be between 0 and 5")

        with db_transaction_manager(db) as transaction_db:
            new_review = Review(
                session_id=session_id,
                reviewer_id=student_id,
                reviewed_user_id=db_session.mentor_id,
                rating=rating,
                comment=comment,
            )
            transaction_db.add(new_review)

        return new_review

    def get_mentor_reviews(self, db: Session, mentor_id: UUID) -> Dict[str, Any]:
        reviews = list(
            db.scalars(
                select(Review).where(Review.reviewed_user_id == mentor_id)
            ).all()
        )

        # List comprehension — curriculum requirement
        ratings = [r.rating for r in reviews]
        count = len(ratings)
        avg_rating = sum(ratings) / count if count > 0 else 0.0

        return {
            "mentor_id": str(mentor_id),
            "average_rating": round(avg_rating, 2),
            "review_count": count,
            "reviews": [
                {
                    "id": str(r.id),
                    "reviewer_id": str(r.reviewer_id),
                    "session_id": str(r.session_id),
                    "rating": r.rating,
                    "comment": r.comment,
                }
                for r in reviews
            ],
        }