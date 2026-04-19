"""
app.py — Flask application factory.
Wires together all blueprints and initialises the DB session lifecycle.
"""

import os
from flask import Flask, jsonify

from auth.routes import auth_bp
from sessions.routes import sessions_bp
from db.sessions import init_db


def create_app() -> Flask:
    app = Flask(__name__)

    # Initialise DB (registers teardown for scoped_session)
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(sessions_bp)

    # Reviews blueprint registered when Daniel's module is ready
    try:
        from reviews.routes import reviews_bp
        app.register_blueprint(reviews_bp)
    except ImportError:
        pass

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
    )