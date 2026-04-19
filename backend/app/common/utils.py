import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.common.exceptions import DatabaseTransactionError

logger = logging.getLogger(__name__)

@contextmanager
def db_transaction_manager(session: Session) -> Generator[Session, None, None]:
    """
    A context manager for safely handling database transactions.
    Rolls back on any error and raises a MentorMatchBaseException.
    Demonstrates Exception handling and Context Managers project requirements.
    """
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database transaction failed: {str(e)}")
        raise DatabaseTransactionError(f"Database transaction failed: {str(e)}")
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error during transaction: {str(e)}")
        raise
