from flask import Blueprint, request, jsonify
from uuid import UUID
from app.db.session import get_db
from app.auth.middleware import require_auth
from app.reviews.service import ReviewService
from app.common.exceptions import MentorMatchBaseException
from flask import g

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")
review_service = ReviewService()


@reviews_bp.route("/session/<session_id>", methods=["POST"])
@require_auth
def leave_review(session_id: str):
    """Leave a review for a completed session."""
    data = request.get_json() or {}

    rating = data.get("rating")
    comment = data.get("comment")

    if rating is None:
        return jsonify({"error": "rating is required"}), 400

    try:
        session_uuid = UUID(session_id)
    except ValueError:
        return jsonify({"error": "Invalid session ID"}), 400

    with get_db() as db:
        try:
            review = review_service.create_review(
                db=db,
                session_id=session_uuid,
                student_id=g.current_user_id,
                rating=int(rating),
                comment=comment,
            )
            return jsonify({"message": "Review submitted successfully", "review_id": str(review.id)}), 201
        except MentorMatchBaseException as e:
            return jsonify({"error": e.message}), e.status_code
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@reviews_bp.route("/mentor/<mentor_id>", methods=["GET"])
@require_auth
def get_mentor_reviews(mentor_id: str):
    """Fetch all reviews for a mentor."""
    try:
        mentor_uuid = UUID(mentor_id)
    except ValueError:
        return jsonify({"error": "Invalid mentor ID"}), 400

    with get_db() as db:
        try:
            data = review_service.get_mentor_reviews(db=db, mentor_id=mentor_uuid)
            return jsonify(data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500