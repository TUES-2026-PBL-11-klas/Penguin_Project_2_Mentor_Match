class SessionNotCompletedException(Exception):
    """
    Raised when an operation requires a completed session but it isn't.
    Used by Daniel's reviews service — a review cannot be written for
    an unfinished session.
    """


class SessionNotFoundException(Exception):
    """Raised when a session ID does not exist in the DB."""


class SessionConflictException(Exception):
    """Raised when a requested session time overlaps with an existing one."""


class UnauthorizedSessionActionException(Exception):
    """Raised when a user tries to act on a session they don't own."""


class InvalidSessionStatusTransitionException(Exception):
    """Raised when an invalid status transition is attempted (e.g. confirmed → pending)."""


class MentorUnavailableException(Exception):
    """
    Raised when a student tries to book during a mentor-marked unavailable slot.
    The frontend shows: 'The mentor is unavailable at the selected time.'
    """