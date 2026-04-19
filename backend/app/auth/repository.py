from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.subject import Subject, MentorSubject
from app.db.models.review import Review
from app.db.models.session import Session as SessionModel


class UserRepository:
    """Data access layer — only DB queries, zero business logic."""

    def __init__(self, db: Session) -> None:
        # Encapsulation: private DB session
        self._db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self._db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        self._db.add(user)
        self._db.flush()
        return user

    def update(self, user: User) -> User:
        self._db.flush()
        return user

    def get_mentors(self) -> List[User]:
        """Return all users who have the mentor or both role."""
        return (
            self._db.query(User)
            .filter(User.role.in_(["mentor", "both"]))
            .all()
        )

    def search_mentors(
        self,
        name: Optional[str] = None,
        subject_id: Optional[int] = None,
    ) -> List[User]:
        """
        Filtered mentor search.
        Uses list comprehension + filter() (curriculum requirement).
        """
        query = self._db.query(User).filter(User.role.in_(["mentor", "both"]))

        if subject_id is not None:
            query = (
                query.join(MentorSubject, MentorSubject.mentor_id == User.id)
                .filter(MentorSubject.subject_id == subject_id)
            )

        mentors = query.all()

        # In-memory name filter using list comprehension (curriculum requirement)
        if name:
            name_lower = name.lower()
            mentors = [
                m for m in mentors
                if name_lower in m.first_name.lower()
                or name_lower in m.last_name.lower()
            ]

        return mentors

    def add_subject_to_mentor(self, mentor_id: UUID, subject_id: int) -> MentorSubject:
        ms = MentorSubject(mentor_id=mentor_id, subject_id=subject_id)
        self._db.add(ms)
        self._db.flush()
        return ms

    def get_mentor_subjects(self, mentor_id: UUID) -> List[Subject]:
        return (
            self._db.query(Subject)
            .join(MentorSubject, MentorSubject.subject_id == Subject.id)
            .filter(MentorSubject.mentor_id == mentor_id)
            .all()
        )

    def get_average_rating(self, mentor_id: UUID) -> float:
        """Compute mentor's average rating from all their reviews."""
        ratings = (
            self._db.query(Review.rating)
            .join(SessionModel, Review.session_id == SessionModel.id)
            .filter(SessionModel.mentor_id == mentor_id)
            .all()
        )
        if not ratings:
            return 0.0
        # map() usage — curriculum requirement
        values = list(map(lambda r: r[0], ratings))
        return round(sum(values) / len(values), 2)

    def get_total_sessions(self, mentor_id: UUID) -> int:
        return (
            self._db.query(SessionModel)
            .filter(
                SessionModel.mentor_id == mentor_id,
                SessionModel.status == "completed",
            )
            .count()
        )