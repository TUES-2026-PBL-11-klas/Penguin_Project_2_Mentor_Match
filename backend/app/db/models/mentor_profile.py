from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.availability import Availability
    from app.db.models.mentor_subject import MentorSubject
    from app.db.models.session import Session
    from app.db.models.user import User


class MentorProfile(TimestampMixin, Base):
    __tablename__ = "mentor_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="mentor_profile")
    availabilities: Mapped[list["Availability"]] = relationship(
        "Availability",
        back_populates="mentor_profile",
        cascade="all, delete-orphan",
        foreign_keys="Availability.mentor_profile_id",
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="mentor_profile",
        cascade="all, delete-orphan",
        foreign_keys="Session.mentor_profile_id",
    )
    subject_links: Mapped[list["MentorSubject"]] = relationship(
        "MentorSubject",
        primaryjoin="MentorProfile.user_id == foreign(MentorSubject.mentor_id)",
        back_populates="mentor_profile",
        viewonly=True,
    )
