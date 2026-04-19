# Notifications routes - Даниел
import os
from flask import Blueprint, request, jsonify
from app.db.session import SessionLocal
from app.notifications.service import WebPushNotificationService
from app.common.exceptions import MentorMatchBaseException

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "dummy_private_key")
VAPID_CLAIMS = {"sub": "mailto:" + os.getenv("VAPID_ADMIN_EMAIL", "admin@mentormatch.local")}

notification_service = WebPushNotificationService(VAPID_PRIVATE_KEY, VAPID_CLAIMS)

@notifications_bp.route("/subscribe", methods=["POST"])
def subscribe():
    """Endpoint for frontend to subscribe to Web Push Notifications"""
    data = request.get_json() or {}
    
    # Expected to be parsed from JWT token realistically, mock for now
    user_id = data.get("user_id")
    subscription_info = data.get("subscription")

    if not user_id or not subscription_info:
        return jsonify({"error": "user_id and subscription data are required"}), 400
        
    if "endpoint" not in subscription_info or "keys" not in subscription_info:
        return jsonify({"error": "Invalid subscription format"}), 400

    db = SessionLocal()
    try:
        sub = notification_service.save_subscription(db=db, user_id=user_id, sub_info=subscription_info)
        return jsonify({"message": "Subscribed successfully", "id": sub.id}), 201
    except MentorMatchBaseException as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        return jsonify({"error": "Failed to save subscription"}), 500

@notifications_bp.route("/<int:user_id>", methods=["GET"])
def get_notifications(user_id: int):
    """Endpoint to fetch notifications for a user"""
    db = SessionLocal()
    try:
        data = notification_service.get_user_notifications(db=db, user_id=user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": "An error occurred fetching notifications"}), 500

@notifications_bp.route("/test-dispatch", methods=["POST"])
def test_dispatch():
    """Utility endpoint to test push notification dispatching asynchronously"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    title = data.get("title", "Test Notification")
    message = data.get("message", "This is a test web push dispatch.")
    notif_type = data.get("type", "Test")

    if not user_id:
         return jsonify({"error": "user_id is required"}), 400

    db = SessionLocal()
    try:
        notification_service.send_notification(
            db=db, 
            user_id=user_id, 
            title=title, 
            message=message, 
            type=notif_type
        )
        return jsonify({"message": "Notification dispatched to queues."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
