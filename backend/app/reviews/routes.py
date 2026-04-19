# Reviews routes - Даниел
from flask import Blueprint, request, jsonify
from app.db.session import SessionLocal
from app.reviews.service import ReviewService
from app.common.exceptions import MentorMatchBaseException

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")
review_service = ReviewService()

@reviews_bp.route("/session/<int:session_id>", methods=["POST"])
def leave_review(session_id: int):
    """Endpoint to leave a review for a mentor."""
    data = request.get_json() or {}
    
    student_id = data.get("student_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not student_id or rating is None:
        return jsonify({"error": "student_id and rating are required"}), 400

    db = SessionLocal()
    try:
        review = review_service.create_review(
            db=db, 
            session_id=session_id, 
            student_id=student_id, 
            rating=int(rating), 
            comment=comment
        )
        return jsonify({"message": "Review submitted successfully", "review_id": review.id}), 201
    except MentorMatchBaseException as e:
        return jsonify({"error": e.message}), e.status_code
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@reviews_bp.route("/mentor/<int:mentor_id>", methods=["GET"])
def get_mentor_reviews(mentor_id: int):
    """Endpoint to fetch aggregate review stats and specific reviews for a mentor."""
    db = SessionLocal()
    try:
        data = review_service.get_mentor_reviews(db=db, mentor_id=mentor_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": "An error occurred fetching reviews"}), 500