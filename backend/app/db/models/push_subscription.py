import uuid

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class PushSubscription(Base):
    """
    Stores a browser Web Push subscription for a user.
    One user can have multiple subscriptions (different devices/browsers).
    """
    __tablename__ = "push_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    endpoint = Column(Text, nullable=False)
    auth = Column(String(255), nullable=False)
    p256dh = Column(String(255), nullable=False)

    user = relationship("User", backref="push_subscriptions")

    def __repr__(self) -> str:
        return f"<PushSubscription user={self.user_id}>"