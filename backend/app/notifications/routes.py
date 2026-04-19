import os
from flask import Blueprint, request, jsonify, g
from uuid import UUID
from app.db.session import get_db
from app.auth.middleware import require_auth
from app.notifications.service import WebPushNotificationService
from app.common.exceptions import MentorMatchBaseException

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "dummy_private_key")
VAPID_CLAIMS = {"sub": "mailto:" + os.getenv("VAPID_ADMIN_EMAIL", "admin@mentormatch.local")}

notification_service = WebPushNotificationService(VAPID_PRIVATE_KEY, VAPID_CLAIMS)


@notifications_bp.route("/subscribe", methods=["POST"])
@require_auth
def subscribe():
    """Subscribe to Web Push Notifications."""
    data = request.get_json() or {}
    subscription_info = data.get("subscription")

    if not subscription_info:
        return jsonify({"error": "subscription data is required"}), 400
    if "endpoint" not in subscription_info or "keys" not in subscription_info:
        return jsonify({"error": "Invalid subscription format"}), 400

    with get_db() as db:
        try:
            sub = notification_service.save_subscription(
                db=db, user_id=g.current_user_id, sub_info=subscription_info
            )
            return jsonify({"message": "Subscribed successfully", "id": str(sub.id)}), 201
        except MentorMatchBaseException as e:
            return jsonify({"error": e.message}), e.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@notifications_bp.route("/", methods=["GET"])
@require_auth
def get_notifications():
    """Fetch notifications for the logged-in user."""
    with get_db() as db:
        try:
            data = notification_service.get_user_notifications(db=db, user_id=g.current_user_id)
            return jsonify(data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@notifications_bp.route("/test-dispatch", methods=["POST"])
@require_auth
def test_dispatch():
    """Test push notification dispatching."""
    data = request.get_json() or {}
    title = data.get("title", "Test Notification")
    message = data.get("message", "This is a test.")
    notif_type = data.get("type", "Test")

    with get_db() as db:
        try:
            notification_service.send_notification(
                db=db,
                user_id=g.current_user_id,
                title=title,
                message=message,
                type=notif_type,
            )
            return jsonify({"message": "Notification dispatched."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500