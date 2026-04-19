from uuid import UUID

from flask import Blueprint, g, jsonify, request

from auth.middleware import require_auth, require_mentor
from auth.service import (
    AuthenticationError,
    RoleAlreadyAssignedError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)
from db.sessions import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    POST /api/auth/register
    Body: { email, password, first_name, last_name, grade, class_letter, role, subject_ids? }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ["email", "password", "first_name", "last_name", "grade", "class_letter", "role"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        with get_db() as db:
            svc = UserService(db)
            user = svc.register(
                email=data["email"],
                password=data["password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                grade=int(data["grade"]),
                class_letter=data["class_letter"],
                role=data["role"],
                subject_ids=data.get("subject_ids"),
            )
            return jsonify({"message": "Registered successfully", "user_id": str(user.id)}), 201
    except UserAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: { email, password }
    Returns: { access_token, token_type }
    """
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password required"}), 400

    try:
        with get_db() as db:
            svc = UserService(db)
            token_data = svc.login(data["email"], data["password"])
            return jsonify(token_data), 200
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/profile", methods=["GET"])
@require_auth
def get_profile():
    """GET /api/auth/profile — returns the logged-in user's profile."""
    with get_db() as db:
        svc = UserService(db)
        try:
            profile = svc.get_profile(g.current_user_id)
            return jsonify(profile), 200
        except UserNotFoundError as e:
            return jsonify({"error": str(e)}), 404


@auth_bp.route("/profile", methods=["PATCH"])
@require_auth
def update_profile():
    """PATCH /api/auth/profile — update bio or profile picture."""
    data = request.get_json() or {}
    with get_db() as db:
        svc = UserService(db)
        try:
            svc.update_profile(
                g.current_user_id,
                bio=data.get("bio"),
                profile_picture=data.get("profile_picture"),
            )
            return jsonify({"message": "Profile updated"}), 200
        except UserNotFoundError as e:
            return jsonify({"error": str(e)}), 404


@auth_bp.route("/add-role", methods=["POST"])
@require_auth
def add_role():
    """
    POST /api/auth/add-role
    Body: { role: "mentor" | "student", subject_ids?: [...] }
    Adds the opposite role to the user (the 'add role' button from Mentor_Match_Logic).
    """
    data = request.get_json() or {}
    new_role = data.get("role")
    if new_role not in ("mentor", "student"):
        return jsonify({"error": "role must be 'mentor' or 'student'"}), 400

    with get_db() as db:
        svc = UserService(db)
        try:
            user = svc.add_role(g.current_user_id, new_role, data.get("subject_ids"))
            return jsonify({"message": "Role added", "new_role": user.role}), 200
        except (UserNotFoundError, RoleAlreadyAssignedError) as e:
            return jsonify({"error": str(e)}), 400


@auth_bp.route("/mentors", methods=["GET"])
@require_auth
def list_mentors():
    """
    GET /api/auth/mentors?name=...&subject_id=...
    Search/list mentors (requires auth).
    """
    name = request.args.get("name")
    subject_id = request.args.get("subject_id", type=int)

    with get_db() as db:
        svc = UserService(db)
        mentors = svc.get_mentor_list(name=name, subject_id=subject_id)
        return jsonify(mentors), 200


@auth_bp.route("/mentors/<mentor_id>", methods=["GET"])
@require_auth
def get_mentor_profile(mentor_id: str):
    """GET /api/auth/mentors/<id> — full mentor profile for the detail page."""
    try:
        mid = UUID(mentor_id)
    except ValueError:
        return jsonify({"error": "Invalid mentor ID"}), 400

    with get_db() as db:
        svc = UserService(db)
        try:
            profile = svc.get_profile(mid)
            return jsonify(profile), 200
        except UserNotFoundError as e:
            return jsonify({"error": str(e)}), 404


@auth_bp.route("/subjects", methods=["GET"])
def list_subjects():
    """GET /api/auth/subjects — list all subjects (public, used during registration)."""
    with get_db() as db:
        svc = UserService(db)
        subjects = svc.get_all_subjects()
        return jsonify(subjects), 200