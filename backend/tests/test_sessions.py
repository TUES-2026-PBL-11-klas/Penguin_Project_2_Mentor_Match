import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import uuid

from app.sessions.service import SessionService, SessionEventObserver

from app.sessions.state_machine import SessionStateMachine

from app.sessions.exceptions import (
    InvalidSessionStatusTransitionException,
    SessionNotFoundException,
    UnauthorizedSessionActionException,
)
from app.sessions.matching import (
    RatingBasedStrategy,
    SubjectFilterStrategy,
    build_matcher,
)


class TestSessionStateMachine:
    def test_pending_to_confirmed(self):
        sm = SessionStateMachine("pending")
        assert sm.transition("confirmed") == "confirmed"

    def test_pending_to_declined(self):
        sm = SessionStateMachine("pending")
        assert sm.transition("declined") == "declined"

    def test_pending_to_cancelled(self):
        sm = SessionStateMachine("pending")
        assert sm.transition("cancelled") == "cancelled"

    def test_confirmed_to_completed(self):
        sm = SessionStateMachine("confirmed")
        assert sm.transition("completed") == "completed"

    def test_confirmed_to_cancelled(self):
        sm = SessionStateMachine("confirmed")
        assert sm.transition("cancelled") == "cancelled"

    def test_completed_is_terminal(self):
        sm = SessionStateMachine("completed")
        assert sm.is_terminal() is True

    def test_declined_is_terminal(self):
        sm = SessionStateMachine("declined")
        assert sm.is_terminal() is True

    def test_cancelled_is_terminal(self):
        sm = SessionStateMachine("cancelled")
        assert sm.is_terminal() is True

    def test_invalid_transition_raises(self):
        sm = SessionStateMachine("completed")
        with pytest.raises(InvalidSessionStatusTransitionException):
            sm.transition("confirmed")

    def test_confirmed_to_pending_raises(self):
        sm = SessionStateMachine("confirmed")
        with pytest.raises(InvalidSessionStatusTransitionException):
            sm.transition("pending")

    def test_can_transition_to_true(self):
        sm = SessionStateMachine("pending")
        assert sm.can_transition_to("confirmed") is True

    def test_can_transition_to_false(self):
        sm = SessionStateMachine("completed")
        assert sm.can_transition_to("cancelled") is False

    def test_status_property(self):
        sm = SessionStateMachine("pending")
        assert sm.status == "pending"


class _FakeUser:
    def __init__(self, rating=0.0, grade=10, subjects=None):
        self.id = uuid.uuid4()
        self._rating = rating
        self.grade = grade
        self._subjects = subjects or []


class TestRatingBasedStrategy:
    def test_sorts_descending(self):
        u1 = _FakeUser(rating=3.0)
        u2 = _FakeUser(rating=5.0)
        u3 = _FakeUser(rating=1.0)
        strategy = RatingBasedStrategy()
        ctx = {"avg_ratings": {u1.id: 3.0, u2.id: 5.0, u3.id: 1.0}}
        result = strategy.match([u1, u2, u3], ctx)
        assert result[0].id == u2.id
        assert result[1].id == u1.id
        assert result[2].id == u3.id

    def test_empty_list(self):
        strategy = RatingBasedStrategy()
        assert strategy.match([], {}) == []

    def test_missing_rating_defaults_to_zero(self):
        u1 = _FakeUser()
        strategy = RatingBasedStrategy()
        result = strategy.match([u1], {"avg_ratings": {}})
        assert result == [u1]


class TestSubjectFilterStrategy:
    def test_filters_by_subject(self):
        u1 = _FakeUser(rating=4.0)
        u2 = _FakeUser(rating=5.0)
        strategy = SubjectFilterStrategy()
        ctx = {
            "subject_id": 1,
            "avg_ratings": {u1.id: 4.0, u2.id: 5.0},
            "mentor_subject_map": {u1.id: [1, 2], u2.id: [3]},
        }
        result = strategy.match([u1, u2], ctx)
        assert len(result) == 1
        assert result[0].id == u1.id

    def test_no_subject_returns_all(self):
        u1 = _FakeUser()
        strategy = SubjectFilterStrategy()
        ctx = {"subject_id": None, "avg_ratings": {}, "mentor_subject_map": {}}
        result = strategy.match([u1], ctx)
        assert result == [u1]

    def test_sorts_by_rating_after_filter(self):
        u1 = _FakeUser(rating=2.0)
        u2 = _FakeUser(rating=4.0)
        strategy = SubjectFilterStrategy()
        ctx = {
            "subject_id": 1,
            "avg_ratings": {u1.id: 2.0, u2.id: 4.0},
            "mentor_subject_map": {u1.id: [1], u2.id: [1]},
        }
        result = strategy.match([u1, u2], ctx)
        assert result[0].id == u2.id


class TestMentorMatcher:
    def test_build_matcher_with_subject(self):
        matcher = build_matcher(subject_id=1)
        assert isinstance(matcher._strategy, SubjectFilterStrategy)

    def test_build_matcher_without_subject(self):
        matcher = build_matcher()
        assert isinstance(matcher._strategy, RatingBasedStrategy)

    def test_set_strategy(self):
        matcher = build_matcher()
        matcher.set_strategy(SubjectFilterStrategy())
        assert isinstance(matcher._strategy, SubjectFilterStrategy)

    def test_match_delegates_to_strategy(self):
        u1 = _FakeUser(rating=5.0)
        matcher = build_matcher()
        ctx = {"avg_ratings": {u1.id: 5.0}}
        result = matcher.match([u1], ctx)
        assert result == [u1]


class TestSessionService:
    def _make_service(self):
        mock_db = MagicMock()
        svc = SessionService(mock_db)
        return svc, mock_db

    def test_observer_registration(self):
        svc, _ = self._make_service()
        observer = SessionEventObserver()
        svc.register_observer(observer)
        assert observer in svc._observers

    def test_notify_calls_observer(self):
        svc, _ = self._make_service()
        called = []

        class TestObserver(SessionEventObserver):
            def on_session_requested(self, session):
                called.append(session)

        svc.register_observer(TestObserver())
        mock_session = MagicMock()
        svc._notify("on_session_requested", mock_session)
        assert len(called) == 1

    def test_get_mentor_calendar_empty(self):
        svc, mock_db = self._make_service()
        with patch.object(svc._repo, 'get_mentor_sessions', return_value=[]):
            result = svc.get_mentor_calendar(uuid.uuid4())
            assert result == []

    def test_get_student_calendar_empty(self):
        svc, mock_db = self._make_service()
        with patch.object(svc._repo, 'get_mentee_sessions', return_value=[]):
            result = svc.get_student_calendar(uuid.uuid4())
            assert result == []

    def test_get_pending_requests_empty(self):
        svc, mock_db = self._make_service()
        with patch.object(svc._repo, 'get_pending_requests_for_mentor', return_value=[]):
            result = svc.get_pending_requests(uuid.uuid4())
            assert result == []

    def test_cancel_session_not_found_raises(self):
        svc, mock_db = self._make_service()
        with patch.object(svc._repo, 'get_by_id', return_value=None):
            with pytest.raises(SessionNotFoundException):
                svc.cancel_session(uuid.uuid4(), uuid.uuid4())

    def test_cancel_session_unauthorized_raises(self):
        svc, mock_db = self._make_service()
        mock_session = MagicMock()
        mock_session.mentor_id = uuid.uuid4()
        mock_session.mentee_id = uuid.uuid4()
        mock_session.status = "confirmed"
        with patch.object(svc._repo, 'get_by_id', return_value=mock_session):
            with pytest.raises(UnauthorizedSessionActionException):
                svc.cancel_session(mock_session.id, uuid.uuid4())

    def test_add_unavailable_slot(self):
        svc, mock_db = self._make_service()
        mentor_id = uuid.uuid4()
        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(hours=2)
        mock_slot = MagicMock()
        with patch.object(svc._repo, 'add_unavailable_slot', return_value=mock_slot):
            svc.add_unavailable_slot(mentor_id, start, end, reason="Test")
            svc._repo.add_unavailable_slot.assert_called_once()

    def test_get_unavailable_slots_empty(self):
        svc, mock_db = self._make_service()
        with patch.object(svc._repo, 'get_unavailable_slots', return_value=[]):
            result = svc.get_unavailable_slots(uuid.uuid4())
            assert result == []
