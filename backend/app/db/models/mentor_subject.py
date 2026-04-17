from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base
from app.db.models.user import mentor_subjects

if TYPE_CHECKING:
    from app.db.models.mentor_profile import MentorProfile
    from app.db.models.subject import Subject


class MentorSubject(Base):
    __table__ = mentor_subjects

    mentor_profile: Mapped["MentorProfile | None"] = relationship(
        "MentorProfile",
        primaryjoin="foreign(MentorSubject.mentor_id) == remote(MentorProfile.user_id)",
        back_populates="subject_links",
        viewonly=True,
    )
    subject: Mapped["Subject"] = relationship(
        "Subject",
        back_populates="mentor_links",
        overlaps="mentors,subjects",
    )
