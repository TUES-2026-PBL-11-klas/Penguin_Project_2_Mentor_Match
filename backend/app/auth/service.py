import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import UUID

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.auth.repository import UserRepository
from app.db.models.user import User
from app.db.models.subject import Subject

JWT_SECRET = os.environ.get("JWT_SECRET", "change_me_in_production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


# ---------------------------------------------------------------------------
# Custom Exceptions (curriculum requirement)
# ---------------------------------------------------------------------------

class AuthenticationError(Exception):
    """Raised when login credentials are invalid."""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to register with an existing email."""


class UserNotFoundError(Exception):
    """Raised when a requested user does not exist."""


class RoleAlreadyAssignedError(Exception):
    """Raised when a user tries to add a role they already have."""


# ---------------------------------------------------------------------------
# Auth Service
# ---------------------------------------------------------------------------

class UserService:
    """
    SOLID - Single Responsibility Principle (SRP):
    # SRP: Handles only user business logic. DB access is delegated to UserRepository.

    SOLID - Dependency Inversion Principle (DIP):
    # DIP: Depends on the UserRepository abstraction, not a concrete DB implementation.
    """

    def __init__(self, db: Session) -> None:
        self._repo = UserRepository(db)
        self._db = db

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        grade: int,
        class_letter: str,
        role: str,
        subject_ids: Optional[List[int]] = None,
    ) -> User:
        """
        Register a new user.
        Typed generics: Optional[List[int]] for subject_ids.
        """
        if self._repo.get_by_email(email):
            raise UserAlreadyExistsError(f"Email {email} is already registered.")

        if not (8 <= grade <= 12):
            raise ValueError("Grade must be between 8 and 12.")
        if class_letter.upper() not in list("ABCDEFG"):
            raise ValueError("Class letter must be A-G.")
        if role not in ("student", "mentor", "both"):
            raise ValueError("Role must be student, mentor, or both.")

        hashed = self._hash_password(password)

        user = User(
            email=email.lower().strip(),
            password_hash=hashed,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            grade=grade,
            class_letter=class_letter.upper(),
            role=role,
        )
        self._repo.create(user)

        if role in ("mentor", "both") and subject_ids:
            for sid in subject_ids:
                self._repo.add_subject_to_mentor(user.id, sid)

        self._db.commit()
        self._db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def login(self, email: str, password: str) -> Dict[str, str]:
        """
        Authenticate user and return a JWT token dict.
        Typed generics: Dict[str, str] return type.
        """
        user = self._repo.get_by_email(email.lower().strip())
        if not user:
            raise AuthenticationError("Invalid email or password.")
        if not self._verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        token = self._generate_token(user)
        return {"access_token": token, "token_type": "Bearer"}

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    def get_profile(self, user_id: UUID) -> Dict:
        """Return enriched profile dict for the given user."""
        user = self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found.")

        profile: Dict = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "grade": user.grade,
            "class_letter": user.class_letter,
            "role": user.role,
            "profile_picture": user.profile_picture,
        }

        if user.is_mentor:
            subjects = self._repo.get_mentor_subjects(user.id)
            # list comprehension — curriculum requirement
            profile["subjects"] = [{"id": s.id, "name": s.name} for s in subjects]
            profile["average_rating"] = self._repo.get_average_rating(user.id)
            profile["total_sessions"] = self._repo.get_total_sessions(user.id)

        return profile

    def update_profile(
        self,
        user_id: UUID,
        bio: Optional[str] = None,
        profile_picture: Optional[str] = None,
    ) -> User:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found.")
        if bio is not None:
            user.bio = bio
        if profile_picture is not None:
            user.profile_picture = profile_picture
        self._repo.update(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def add_role(
        self,
        user_id: UUID,
        new_role: str,
        subject_ids: Optional[List[int]] = None,
    ) -> User:
        """
        Allow a student to become a mentor (or vice versa).
        Corresponds to the 'add role' button in Mentor_Match_Logic.
        """
        user = self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found.")
        if user.role == "both":
            raise RoleAlreadyAssignedError("User already has both roles.")
        if user.role == new_role:
            raise RoleAlreadyAssignedError(f"User already has role '{new_role}'.")

        user.role = "both"
        if new_role == "mentor" and subject_ids:
            for sid in subject_ids:
                self._repo.add_subject_to_mentor(user.id, sid)

        self._db.commit()
        self._db.refresh(user)
        return user

    def get_mentor_list(
        self,
        name: Optional[str] = None,
        subject_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Return list of mentors with summary info for the search page.
        Uses map() — curriculum requirement.
        """
        mentors = self._repo.search_mentors(name=name, subject_id=subject_id)

        return list(map(
            lambda m: {
                "id": str(m.id),
                "first_name": m.first_name,
                "last_name": m.last_name,
                "grade": m.grade,
                "class_letter": m.class_letter,
                "average_rating": self._repo.get_average_rating(m.id),
                "total_sessions": self._repo.get_total_sessions(m.id),
            },
            mentors,
        ))

    def get_all_subjects(self) -> List[Dict]:
        subjects = self._db.query(Subject).order_by(Subject.name).all()
        return [{"id": s.id, "name": s.name, "category": s.category} for s in subjects]

    # ------------------------------------------------------------------
    # JWT helpers — private (encapsulation)
    # ------------------------------------------------------------------

    def _hash_password(self, password: str) -> str:
        """Encapsulation: password hashing is a private implementation detail."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def _verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def _generate_token(self, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Dict:
        """Decode and validate a JWT."""
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])