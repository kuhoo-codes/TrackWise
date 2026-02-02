from src.exceptions.base import BaseCustomException


class AIServiceError(BaseCustomException):
    """Raised when there is a general AI service error."""

    def __init__(self, message: str = "AI service error", details: dict = None) -> None:
        super().__init__(message=message, status_code=500, error_code="AI_SERVICE_ERROR", details=details)
