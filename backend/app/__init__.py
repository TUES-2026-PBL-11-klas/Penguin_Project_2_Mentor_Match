import os

from flask import Flask

from app.db import init_db
from app.seed import register_seed_commands


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["DATABASE_URL"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@db:5432/mentormatch",
    )
    init_db(app)
    register_seed_commands(app)
    return app
