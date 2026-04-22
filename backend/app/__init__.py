import os
import logging

from flask import Flask, jsonify
from app.db import init_db
from app.seed import register_seed_commands
from prometheus_flask_exporter import PrometheusMetrics

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ]
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["DATABASE_URL"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@db:5432/mentormatch",  # pragma: allowlist secret
    )

    PrometheusMetrics(app)
    init_db(app)
    register_seed_commands(app)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.sessions.routes import sessions_bp
    app.register_blueprint(sessions_bp)

    from app.reviews.routes import reviews_bp
    from app.notifications.routes import notifications_bp
    app.register_blueprint(reviews_bp)
    app.register_blueprint(notifications_bp)

    from app.scheduler import start_scheduler
    start_scheduler()

    return app
