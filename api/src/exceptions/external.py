from src.exceptions.base import BaseCustomException


class ExternalServiceError(BaseCustomException):
    """Raised when external service fails."""

    def __init__(self, message: str = "External service error", details: dict = None) -> None:
        super().__init__(message=message, status_code=502, error_code="EXTERNAL_SERVICE_ERROR", details=details)


class GitHubIntegrationError(BaseCustomException):
    """Raised when GitHub integration fails."""

    def __init__(self, message: str = "GitHub integration error", details: dict = None) -> None:
        super().__init__(message=message, status_code=502, error_code="GITHUB_INTEGRATION_ERROR", details=details)
