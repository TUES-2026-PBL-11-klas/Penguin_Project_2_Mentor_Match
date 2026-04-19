# Notifications service - Даниел
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from pywebpush import webpush, WebPushException
import concurrent.futures

from app.db.models.notification import Notification
from app.db.models.push_subscription import PushSubscription
from app.common.utils import db_transaction_manager

logger = logging.getLogger(__name__)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

class INotificationService(ABC):
    """Abstract Base Class for Notifications (OOP Abstraction, SOLID Open/Closed)"""
    @abstractmethod
    def save_subscription(self, db: Session, user_id: int, sub_info: Dict[str, Any]) -> PushSubscription:
        pass

    @abstractmethod
    def send_notification(self, db: Session, user_id: int, title: str, message: str, type: str, session_id: int = None) -> None:
        pass
    
    @abstractmethod
    def get_user_notifications(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        pass

class WebPushNotificationService(INotificationService):
    def __init__(self, vapid_private_key: str, vapid_claims: Dict[str, str]):
        self.vapid_private_key = vapid_private_key
        self.vapid_claims = vapid_claims

    def save_subscription(self, db: Session, user_id: int, sub_info: Dict[str, Any]) -> PushSubscription:
        with db_transaction_manager(db) as transaction_db:
            # Check if exists
            existing = transaction_db.scalars(
                select(PushSubscription).where(
                    PushSubscription.user_id == user_id, 
                    PushSubscription.endpoint == sub_info["endpoint"]
                )
            ).first()
            if existing: # if exists update auth tokens just in case
                existing.auth = sub_info["keys"]["auth"]
                existing.p256dh = sub_info["keys"]["p256dh"]
                return existing

            subscription = PushSubscription(
                user_id=user_id,
                endpoint=sub_info["endpoint"],
                auth=sub_info["keys"]["auth"],
                p256dh=sub_info["keys"]["p256dh"]
            )
            transaction_db.add(subscription)
        return subscription
        
    def _dispatch_push(self, subscription_info: Dict[str, Any], payload: str):
        """Internal synchronous task to send push notification"""
        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            logger.info("Web push sent successfully.")
        except WebPushException as ex:
            logger.error(f"Web push failed: {repr(ex)}")

    def send_notification(self, db: Session, user_id: int, title: str, message: str, type: str, session_id: int | None = None) -> None:
        """Saves notification in DB and dispatches via Async executor"""
        # Save to DB first
        with db_transaction_manager(db) as transaction_db:
            notif = Notification(
                user_id=user_id,
                session_id=session_id,
                type=type,
                message=message,
                is_read=False
            )
            transaction_db.add(notif)
        
        # Get subs
        subs = db.scalars(select(PushSubscription).where(PushSubscription.user_id == user_id)).all()
        
        if not subs:
            return

        payload = json.dumps({"title": title, "body": message, "type": type})

        for sub in subs:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }
            # Trigger async thread execution to not block main API response
            executor.submit(self._dispatch_push, sub_info, payload)

    def get_user_notifications(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        notifs = db.scalars(select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())).all()
        return [
            {
                "id": n.id,
                "type": n.type,
                "message": n.message,
                "is_read": n.is_read,
                "session_id": n.session_id,
                "created_at": n.created_at.isoformat() if hasattr(n, 'created_at') else None
            }
            for n in notifs
        ]