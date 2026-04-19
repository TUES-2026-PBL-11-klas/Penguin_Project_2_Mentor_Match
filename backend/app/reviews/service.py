# Reviews service - Даниел
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.review import Review
from app.db.models.session import Session as DbSession
from app.common.exceptions import ReviewAlreadyExistsException, SessionNotCompletedException
from app.common.utils import db_transaction_manager

class IReviewService(ABC):
    """Abstract Base Class for ReviewService (SOLID - Dependency Inversion)"""
    @abstractmethod
    def create_review(self, db: Session, session_id: int, student_id: int, rating: int, comment: str | None = None) -> Review:
        pass

    @abstractmethod
    def get_mentor_reviews(self, db: Session, mentor_id: int) -> Dict[str, Any]:
        pass

class ReviewService(IReviewService):
    def create_review(self, db: Session, session_id: int, student_id: int, rating: int, comment: str | None = None) -> Review:
        db_session = db.scalars(select(DbSession).where(DbSession.id == session_id)).first()
        if not db_session:
            raise ValueError("Session not found")
        if db_session.student_id != student_id:
            raise ValueError("Unauthorized student for this session")
        if db_session.status != "completed":
            raise SessionNotCompletedException()
        
        existing_review = db.scalars(select(Review).where(Review.session_id == session_id)).first()
        if existing_review:
            raise ReviewAlreadyExistsException()

        with db_transaction_manager(db) as transaction_db:
            new_review = Review(
                session_id=session_id,
                mentor_id=db_session.mentor_id,
                student_id=student_id,
                rating=rating,
                comment=comment,
            )
            transaction_db.add(new_review)
            
        return new_review

    def get_mentor_reviews(self, db: Session, mentor_id: int) -> Dict[str, Any]:
        reviews = list(db.scalars(select(Review).where(Review.mentor_id == mentor_id)).all())
        
        # List comprehension and generator expression usage
        ratings = [r.rating for r in reviews]
        count = len(ratings)
        avg_rating = sum(ratings) / count if count > 0 else 0.0

        return {
            "mentor_id": mentor_id,
            "average_rating": round(avg_rating, 2),
            "review_count": count,
            "reviews": [
                {
                    "id": r.id,
                    "student_id": r.student_id,
                    "session_id": r.session_id,
                    "rating": r.rating,
                    "comment": r.comment,
                }
                for r in reviews
            ]
        }