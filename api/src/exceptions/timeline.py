from src.exceptions.base import BaseCustomException


class TimelineNotFoundError(BaseCustomException):
    """Raised when a timeline is not found."""

    def __init__(self, message: str = "Timeline not found", details: dict = None) -> None:
        super().__init__(message=message, status_code=404, error_code="TIMELINE_NOT_FOUND", details=details)


class TimelineNodeNotFoundError(BaseCustomException):
    """Raised when a timeline node is not found."""

    def __init__(self, message: str = "Timeline node not found", details: dict = None) -> None:
        super().__init__(message=message, status_code=404, error_code="TIMELINE_NODE_NOT_FOUND", details=details)


class InvalidTimelineNodeError(BaseCustomException):
    """Raised when a timeline node is invalid."""

    def __init__(self, message: str = "Invalid timeline node", details: dict = None) -> None:
        super().__init__(message=message, status_code=400, error_code="INVALID_TIMELINE_NODE", details=details)
