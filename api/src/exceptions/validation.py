from src.exceptions.base import BaseCustomException


class ValidationError(BaseCustomException):
    """Raised when validation fails."""

    def __init__(self, message: str = "Validation failed", details: dict = None) -> None:
        super().__init__(message=message, status_code=422, error_code="VALIDATION_ERROR", details=details)
