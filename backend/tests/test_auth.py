import pytest
from unittest.mock import MagicMock, patch
import uuid
from app.auth.service import (
    UserService,
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    RoleAlreadyAssignedError,
)
from app.db.models.user import User


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def sample_user():
    import bcrypt
    hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@test.com"
    user.password_hash = hashed
    user.first_name = "Test"
    user.last_name = "User"
    user.grade = 10
    user.class_letter = "A"
    user.role = "student"
    user.is_mentor = False
    user.is_student = True
    user.bio = None
    user.profile_picture = None
    return user


class TestRegistration:
    def test_register_invalid_grade_raises(self, mock_db):
        mock_db.query().filter().first.return_value = None
        svc = UserService(mock_db)
        with pytest.raises(ValueError, match="Grade"):
            svc.register("a@b.com", "pass", "A", "B", 7, "A", "student")

    def test_register_invalid_class_raises(self, mock_db):
        mock_db.query().filter().first.return_value = None
        svc = UserService(mock_db)
        with pytest.raises(ValueError, match="Class"):
            svc.register("a@b.com", "pass", "A", "B", 10, "Z", "student")

    def test_register_invalid_role_raises(self, mock_db):
        mock_db.query().filter().first.return_value = None
        svc = UserService(mock_db)
        with pytest.raises(ValueError, match="Role"):
            svc.register("a@b.com", "pass", "A", "B", 10, "A", "teacher")

    def test_register_duplicate_email_raises(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user
        svc = UserService(mock_db)
        with pytest.raises(UserAlreadyExistsError):
            svc.register("test@test.com", "pass", "A", "B", 10, "A", "student")


class TestLogin:
    def test_login_wrong_email_raises(self, mock_db):
        mock_db.query().filter().first.return_value = None
        svc = UserService(mock_db)
        with pytest.raises(AuthenticationError):
            svc.login("wrong@test.com", "password123")

    def test_login_wrong_password_raises(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user
        svc = UserService(mock_db)
        with pytest.raises(AuthenticationError):
            svc.login("test@test.com", "wrongpassword")

    def test_login_success_returns_token(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user
        svc = UserService(mock_db)
        result = svc.login("test@test.com", "password123")
        assert "access_token" in result
        assert result["token_type"] == "Bearer"

    def test_token_decode(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user
        svc = UserService(mock_db)
        result = svc.login("test@test.com", "password123")
        payload = UserService.decode_token(result["access_token"])
        assert payload["email"] == "test@test.com"
        assert payload["role"] == "student"


class TestProfile:
    def test_get_profile_user_not_found_raises(self, mock_db):
        mock_db.query().filter().first.return_value = None
        svc = UserService(mock_db)
        with pytest.raises(UserNotFoundError):
            svc.get_profile(uuid.uuid4())

    def test_get_profile_student(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user
        svc = UserService(mock_db)
        with patch.object(svc._repo, 'get_by_id', return_value=sample_user):
            profile = svc.get_profile(sample_user.id)
            assert profile["email"] == "test@test.com"
            assert profile["role"] == "student"

    def test_get_profile_mentor_has_subjects(self, mock_db, sample_user):
        sample_user.role = "mentor"
        sample_user.is_mentor = True
        mock_db.query().filter().first.return_value = sample_user
        svc = UserService(mock_db)
        with patch.object(svc._repo, 'get_by_id', return_value=sample_user), \
             patch.object(svc._repo, 'get_mentor_subjects', return_value=[]), \
             patch.object(svc._repo, 'get_average_rating', return_value=0.0), \
             patch.object(svc._repo, 'get_total_sessions', return_value=0):
            profile = svc.get_profile(sample_user.id)
            assert "subjects" in profile
            assert "average_rating" in profile


class TestAddRole:
    def test_add_role_both_raises(self, mock_db, sample_user):
        sample_user.role = "both"
        svc = UserService(mock_db)
        with patch.object(svc._repo, 'get_by_id', return_value=sample_user):
            with pytest.raises(RoleAlreadyAssignedError):
                svc.add_role(sample_user.id, "mentor")

    def test_add_same_role_raises(self, mock_db, sample_user):
        svc = UserService(mock_db)
        with patch.object(svc._repo, 'get_by_id', return_value=sample_user):
            with pytest.raises(RoleAlreadyAssignedError):
                svc.add_role(sample_user.id, "student")

    def test_add_role_success(self, mock_db, sample_user):
        svc = UserService(mock_db)
        with patch.object(svc._repo, 'get_by_id', return_value=sample_user):
            svc.add_role(sample_user.id, "mentor")
            assert sample_user.role == "both"


class TestMentorList:
    def test_get_mentor_list_empty(self, mock_db):
        svc = UserService(mock_db)
        with patch.object(svc._repo, 'search_mentors', return_value=[]):
            result = svc.get_mentor_list()
            assert result == []

    def test_get_mentor_list_returns_mentors(self, mock_db, sample_user):
        sample_user.role = "mentor"
        sample_user.is_mentor = True
        svc = UserService(mock_db)
        with patch.object(svc._repo, 'search_mentors', return_value=[sample_user]), \
             patch.object(svc._repo, 'get_average_rating', return_value=4.5), \
             patch.object(svc._repo, 'get_total_sessions', return_value=3):
            result = svc.get_mentor_list()
            assert len(result) == 1
            assert result[0]["average_rating"] == 4.5
            assert result[0]["total_sessions"] == 3


class TestPasswordHashing:
    def test_hash_and_verify(self, mock_db):
        svc = UserService(mock_db)
        hashed = svc._hash_password("mypassword")
        assert svc._verify_password("mypassword", hashed) is True
        assert svc._verify_password("wrongpassword", hashed) is False
