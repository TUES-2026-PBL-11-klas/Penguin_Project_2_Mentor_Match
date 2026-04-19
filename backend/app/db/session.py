import os
from contextlib import contextmanager

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def get_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    database = os.getenv("POSTGRES_DB", "mentormatch")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


engine = create_engine(get_database_url(), future=True)
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
)


@contextmanager
def get_db():
    """
    Context manager for DB sessions — satisfies the curriculum 'with statement' requirement.

    Usage:
        with get_db() as db:
            users = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        SessionLocal.remove()


def init_db(app: Flask) -> None:
    app.extensions["db_session"] = SessionLocal
    app.extensions["db_engine"] = engine

    @app.teardown_appcontext
    def shutdown_session(_exception=None) -> None:
        SessionLocal.remove()