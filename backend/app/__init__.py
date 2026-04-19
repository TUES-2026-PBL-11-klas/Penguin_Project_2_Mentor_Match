import os
from flask import Flask, jsonify
from app.db import init_db
from app.seed import register_seed_commands

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/app.log"),
        logging.StreamHandler(),
    ]
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["DATABASE_URL"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@db:5432/mentormatch",
    )

    init_db(app)
    register_seed_commands(app)

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # Auth (Stefan + Maya)
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    # Sessions (Maya)
    from app.sessions.routes import sessions_bp
    app.register_blueprint(sessions_bp)

    # Reviews and Notifications (Daniel)
    from app.reviews.routes import reviews_bp
    from app.notifications.routes import notifications_bp
    app.register_blueprint(reviews_bp)
    app.register_blueprint(notifications_bp)

    return app