from sessions.exceptions import InvalidSessionStatusTransitionException

# Valid transitions: current_status → set of allowed next statuses
_VALID_TRANSITIONS: dict[str, set[str]] = {
    "pending":   {"confirmed", "declined", "cancelled"},
    "confirmed": {"completed", "cancelled"},
    "completed": set(),   # terminal
    "declined":  set(),   # terminal
    "cancelled": set(),   # terminal
}


class SessionStateMachine:
    """
    Encapsulates session status transition rules.

    SOLID - SRP:
    # SRP: One job — validate and apply status transitions.
    OOP: Encapsulation — transition rules are private to this class.
    """

    def __init__(self, current_status: str) -> None:
        self._status = current_status

    @property
    def status(self) -> str:
        return self._status

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in _VALID_TRANSITIONS.get(self._status, set())

    def transition(self, new_status: str) -> str:
        """
        Apply the transition and return the new status.
        Raises InvalidSessionStatusTransitionException if the transition is not allowed.
        """
        if not self.can_transition_to(new_status):
            allowed = _VALID_TRANSITIONS.get(self._status, set())
            raise InvalidSessionStatusTransitionException(
                f"Cannot transition from '{self._status}' to '{new_status}'. "
                f"Allowed transitions: {allowed}"
            )
        self._status = new_status
        return self._status

    def is_terminal(self) -> bool:
        return len(_VALID_TRANSITIONS.get(self._status, set())) == 0