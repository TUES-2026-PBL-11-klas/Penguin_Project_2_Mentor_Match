import pytest
from unittest.mock import MagicMock
from app.reviews.service import ReviewService
from app.common.exceptions import SessionNotCompletedException, ReviewAlreadyExistsException
from app.db.models.review import Review
from app.db.models.session import Session as DbSession
import uuid


@pytest.fixture
def review_service():
    return ReviewService()


@pytest.fixture
def mock_db():
    return MagicMock()


def test_create_review_unauthorized(review_service, mock_db):
    mentor_id = uuid.uuid4()
    mentee_id = uuid.uuid4()
    mock_session = DbSession(
        id=uuid.uuid4(), mentee_id=mentee_id, mentor_id=mentor_id, status="completed",
        subject_id=1, scheduled_at=None, end_at=None, duration_minutes=60
    )
    mock_db.scalars().first.return_value = mock_session

    with pytest.raises(ValueError, match="Unauthorized"):
        review_service.create_review(mock_db, session_id=mock_session.id, student_id=uuid.uuid4(), rating=5)


def test_create_review_not_completed(review_service, mock_db):
    mentor_id = uuid.uuid4()
    mentee_id = uuid.uuid4()
    mock_session = DbSession(
        id=uuid.uuid4(), mentee_id=mentee_id, mentor_id=mentor_id, status="pending",
        subject_id=1, scheduled_at=None, end_at=None, duration_minutes=60
    )
    mock_db.scalars().first.return_value = mock_session

    with pytest.raises(SessionNotCompletedException):
        review_service.create_review(mock_db, session_id=mock_session.id, student_id=mentee_id, rating=5)


def test_create_review_already_exists(review_service, mock_db):
    mentor_id = uuid.uuid4()
    mentee_id = uuid.uuid4()
    session_id = uuid.uuid4()
    mock_session = DbSession(
        id=session_id, mentee_id=mentee_id, mentor_id=mentor_id, status="completed",
        subject_id=1, scheduled_at=None, end_at=None, duration_minutes=60
    )
    mock_review = Review(
        id=uuid.uuid4(), session_id=session_id,
        reviewer_id=mentee_id, reviewed_user_id=mentor_id, rating=4
    )
    mock_db.scalars().first.side_effect = [mock_session, mock_review]

    with pytest.raises(ReviewAlreadyExistsException):
        review_service.create_review(mock_db, session_id=session_id, student_id=mentee_id, rating=4)


def test_create_review_success_integration(review_service, mock_db):
    """Integration style test mocking external DB interactions but verifying full app flow."""
    mentor_id = uuid.uuid4()
    mentee_id = uuid.uuid4()
    session_id = uuid.uuid4()
    mock_session = DbSession(
        id=session_id, mentee_id=mentee_id, mentor_id=mentor_id, status="completed",
        subject_id=1, scheduled_at=None, end_at=None, duration_minutes=60
    )
    mock_db.scalars().first.side_effect = [mock_session, None]

    review = review_service.create_review(
        mock_db, session_id=session_id, student_id=mentee_id, rating=4, comment="Great"
    )

    assert review.session_id == session_id
    assert review.reviewed_user_id == mentor_id
    assert review.rating == 4
    assert review.comment == "Great"


def test_get_mentor_reviews(review_service, mock_db):
    mentor_id = uuid.uuid4()
    mentee_id = uuid.uuid4()
    mock_review1 = Review(
        id=uuid.uuid4(), reviewer_id=mentee_id, reviewed_user_id=mentor_id,
        session_id=uuid.uuid4(), rating=4, comment="Good"
    )
    mock_review2 = Review(
        id=uuid.uuid4(), reviewer_id=uuid.uuid4(), reviewed_user_id=mentor_id,
        session_id=uuid.uuid4(), rating=5, comment="Excellent"
    )

    class MockResult:
        def all(self):
            return [mock_review1, mock_review2]

    mock_db.scalars.return_value = MockResult()

    result = review_service.get_mentor_reviews(mock_db, mentor_id=mentor_id)

    assert result["average_rating"] == 4.5
    assert result["review_count"] == 2
    assert len(result["reviews"]) == 2
