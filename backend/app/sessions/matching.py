from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from app.db.models.user import User


# ---------------------------------------------------------------------------
# Abstract Strategy
# ---------------------------------------------------------------------------

class MentorMatchStrategy(ABC):
    """
    OOP Abstraction: abstract base for all matching strategies.
    OOP Polymorphism: subclasses implement match() differently.

    SOLID - Open/Closed Principle (OCP):
    # OCP: Add new strategies without modifying MentorMatcher or any callers.
    """

    @abstractmethod
    def match(self, mentors: List[User], context: Dict) -> List[User]:
        """Filter and/or sort the mentor list."""
        ...


# ---------------------------------------------------------------------------
# Concrete Strategies
# ---------------------------------------------------------------------------

class RatingBasedStrategy(MentorMatchStrategy):
    """Sort mentors by average rating descending. Default strategy."""

    def match(self, mentors: List[User], context: Dict) -> List[User]:
        avg_ratings: Dict[UUID, float] = context.get("avg_ratings", {})
        return sorted(
            mentors,
            key=lambda m: avg_ratings.get(m.id, 0.0),
            reverse=True,
        )


class SubjectFilterStrategy(MentorMatchStrategy):
    """Filter to mentors teaching the requested subject, then sort by rating."""

    def match(self, mentors: List[User], context: Dict) -> List[User]:
        subject_id: Optional[int] = context.get("subject_id")
        avg_ratings: Dict[UUID, float] = context.get("avg_ratings", {})
        mentor_subject_map: Dict[UUID, List[int]] = context.get("mentor_subject_map", {})

        if subject_id is None:
            return mentors

        # filter() — curriculum requirement
        filtered = list(filter(
            lambda m: subject_id in mentor_subject_map.get(m.id, []),
            mentors,
        ))

        return sorted(filtered, key=lambda m: avg_ratings.get(m.id, 0.0), reverse=True)


class GradeProximityStrategy(MentorMatchStrategy):
    """Prefer mentors in same or higher grade than the student."""

    def match(self, mentors: List[User], context: Dict) -> List[User]:
        student_grade: int = context.get("student_grade", 8)
        avg_ratings: Dict[UUID, float] = context.get("avg_ratings", {})

        # list comprehension — curriculum requirement
        preferred = [m for m in mentors if m.grade >= student_grade]
        others    = [m for m in mentors if m.grade < student_grade]

        preferred.sort(key=lambda m: avg_ratings.get(m.id, 0.0), reverse=True)
        others.sort(key=lambda m: avg_ratings.get(m.id, 0.0), reverse=True)

        return preferred + others


# ---------------------------------------------------------------------------
# Context — MentorMatcher
# ---------------------------------------------------------------------------

class MentorMatcher:
    """
    Strategy Pattern context.

    SOLID - DIP:
    # DIP: Depends on MentorMatchStrategy abstraction, not any concrete class.
    """

    def __init__(self, strategy: MentorMatchStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: MentorMatchStrategy) -> None:
        self._strategy = strategy

    def match(self, mentors: List[User], context: Dict) -> List[User]:
        return self._strategy.match(mentors, context)


def build_matcher(subject_id: Optional[int] = None) -> MentorMatcher:
    """Factory: choose the right strategy based on search parameters."""
    if subject_id is not None:
        return MentorMatcher(SubjectFilterStrategy())
    return MentorMatcher(RatingBasedStrategy())