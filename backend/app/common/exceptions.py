class MentorMatchBaseException(Exception):
    """Base exception for the Mentor Match application."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ReviewAlreadyExistsException(MentorMatchBaseException):
    """Raised when a review for a session already exists."""
    def __init__(self, message: str = "A review for this session already exists."):
        super().__init__(message, status_code=409)

class SessionNotCompletedException(MentorMatchBaseException):
    """Raised when trying to review a session that is not completed."""
    def __init__(self, message: str = "Only completed sessions can be reviewed."):
        super().__init__(message, status_code=400)

class DatabaseTransactionError(MentorMatchBaseException):
    """Raised when a database transaction fails."""
    def __init__(self, message: str = "Database transaction failed."):
        super().__init__(message, status_code=500)
