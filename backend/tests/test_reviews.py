import pytest
from unittest.mock import MagicMock
from app.reviews.service import ReviewService
from app.common.exceptions import SessionNotCompletedException, ReviewAlreadyExistsException
from app.db.models.review import Review
from app.db.models.session import Session as DbSession

@pytest.fixture
def review_service():
    return ReviewService()

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

def test_create_review_unauthorized(review_service, mock_db):
    mock_session = DbSession(id=1, student_id=2, mentor_id=3, status="completed")
    mock_db.scalars().first.return_value = mock_session

    with pytest.raises(ValueError, match="Unauthorized student for this session"):
        review_service.create_review(mock_db, session_id=1, student_id=99, rating=5)

def test_create_review_not_completed(review_service, mock_db):
    mock_session = DbSession(id=1, student_id=2, mentor_id=3, status="pending")
    mock_db.scalars().first.return_value = mock_session
    
    with pytest.raises(SessionNotCompletedException):
        review_service.create_review(mock_db, session_id=1, student_id=2, rating=5)

def test_create_review_already_exists(review_service, mock_db):
    mock_session = DbSession(id=1, student_id=2, mentor_id=3, status="completed")
    mock_review = Review(id=1)
    mock_db.scalars().first.side_effect = [mock_session, mock_review]
    
    with pytest.raises(ReviewAlreadyExistsException):
         review_service.create_review(mock_db, session_id=1, student_id=2, rating=4)

def test_create_review_success_integration(review_service, mock_db):
    """Integration style test mocking external DB interactions but verifying full app flow."""
    mock_session = DbSession(id=1, student_id=2, mentor_id=3, status="completed")
    mock_db.scalars().first.side_effect = [mock_session, None]
    
    review = review_service.create_review(mock_db, session_id=1, student_id=2, rating=4, comment="Great")
    
    assert review.session_id == 1
    assert review.mentor_id == 3
    assert review.rating == 4
    assert review.comment == "Great"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_get_mentor_reviews(review_service, mock_db):
    mock_review1 = Review(id=1, student_id=2, session_id=1, rating=4, comment="Good")
    mock_review2 = Review(id=2, student_id=3, session_id=2, rating=5, comment="Excellent")
    
    class MockResult:
        def all(self):
            return [mock_review1, mock_review2]
            
    mock_db.scalars.return_value = MockResult()
    
    result = review_service.get_mentor_reviews(mock_db, mentor_id=3)
    
    assert result["mentor_id"] == 3
    assert result["average_rating"] == 4.5
    assert result["review_count"] == 2
    assert len(result["reviews"]) == 2
