from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.mentor_profile import MentorProfile
    from app.db.models.user import User


class Availability(TimestampMixin, Base):
    __tablename__ = "availabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    mentor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mentor_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("mentor_profiles.id", ondelete="CASCADE")
    )
    day_of_week: Mapped[int | None] = mapped_column(Integer)
    weekday: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    mentor: Mapped["User"] = relationship(
        "User", back_populates="mentor_availabilities", foreign_keys=[mentor_id]
    )
    mentor_profile: Mapped["MentorProfile | None"] = relationship(
        "MentorProfile",
        back_populates="availabilities",
        foreign_keys=[mentor_profile_id],
    )
