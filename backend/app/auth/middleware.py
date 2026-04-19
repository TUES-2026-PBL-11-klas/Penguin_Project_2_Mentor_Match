from functools import wraps
from typing import Callable, Optional
from uuid import UUID

import jwt
from flask import g, jsonify, request

from app.auth.service import UserService
from app.db.models.user import User
from app.db.session import SessionLocal


def get_current_user_id() -> Optional[UUID]:
    """Extract and validate the user ID from the JWT Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        payload = UserService.decode_token(token)
        return UUID(payload["sub"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
        return None


def require_auth(f: Callable) -> Callable:
    """Decorator: requires a valid JWT. Sets g.current_user_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        if user_id is None:
            return jsonify({"error": "Unauthorized"}), 401
        g.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated


def require_mentor(f: Callable) -> Callable:
    """Decorator: requires the user to have the mentor or both role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        if user_id is None:
            return jsonify({"error": "Unauthorized"}), 401

        db = SessionLocal()
        try:
            user: Optional[User] = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_mentor:
                return jsonify({"error": "Mentor role required"}), 403
        finally:
            SessionLocal.remove()

        g.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated


def require_student(f: Callable) -> Callable:
    """Decorator: requires the user to have the student or both role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        if user_id is None:
            return jsonify({"error": "Unauthorized"}), 401

        db = SessionLocal()
        try:
            user: Optional[User] = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_student:
                return jsonify({"error": "Student role required"}), 403
        finally:
            SessionLocal.remove()

        g.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated