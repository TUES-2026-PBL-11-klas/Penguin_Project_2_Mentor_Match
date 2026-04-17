from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.mentor_subject import MentorSubject
    from app.db.models.session import Session
    from app.db.models.user import User


class Subject(TimestampMixin, Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))

    mentors: Mapped[list["User"]] = relationship(
        "User",
        secondary="mentor_subjects",
        back_populates="subjects",
        overlaps="mentor_links,subject",
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="subject",
    )
    mentor_links: Mapped[list["MentorSubject"]] = relationship(
        "MentorSubject",
        back_populates="subject",
        cascade="all, delete-orphan",
        overlaps="mentors,subjects",
    )
