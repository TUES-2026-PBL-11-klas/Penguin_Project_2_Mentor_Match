"""
db/models/base.py — Shared SQLAlchemy declarative base.
All model files import Base from here to share the same metadata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass