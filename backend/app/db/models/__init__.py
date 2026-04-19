"""
db/models/__init__.py — Re-exports all models from one place.

Every other file in the project can keep using:
    from db.models import User, Session, Review, ...

The import order matters here — models with no FK dependencies first,
then models that reference them, so SQLAlchemy can resolve all relationships.
"""

from db.models.base import Base
from db.models.user import User
from db.models.subject import Subject, MentorSubject
from db.models.availability import Availability, UnavailableSlot
from db.models.session import Session
from db.models.review import Review
from db.models.notification import Notification

__all__ = [
    "Base",
    "User",
    "Subject",
    "MentorSubject",
    "Availability",
    "UnavailableSlot",
    "Session",
    "Review",
    "Notification",
]
