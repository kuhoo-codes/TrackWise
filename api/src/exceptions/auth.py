from src.exceptions.base import BaseCustomException


class AuthenticationError(BaseCustomException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: dict = None) -> None:
        super().__init__(message=message, status_code=401, error_code="AUTH_FAILED", details=details)


class AuthorizationError(BaseCustomException):
    """Raised when user lacks permission for an action."""

    def __init__(self, message: str = "Insufficient permissions", details: dict = None) -> None:
        super().__init__(message=message, status_code=403, error_code="INSUFFICIENT_PERMISSIONS", details=details)


class TokenExpiredError(BaseCustomException):
    """Raised when JWT token is expired."""

    def __init__(self, message: str = "Token has expired", details: dict = None) -> None:
        super().__init__(message=message, status_code=401, error_code="TOKEN_EXPIRED", details=details)


class InvalidTokenError(BaseCustomException):
    """Raised when JWT token is invalid."""

    def __init__(self, message: str = "Invalid token", details: dict = None) -> None:
        super().__init__(message=message, status_code=401, error_code="INVALID_TOKEN", details=details)


class UserNotFoundError(BaseCustomException):
    """Raised when user is not found."""

    def __init__(self, message: str = "User not found", details: dict = None) -> None:
        super().__init__(message=message, status_code=404, error_code="USER_NOT_FOUND", details=details)


class UserAlreadyExistsError(BaseCustomException):
    """Raised when trying to create a user that already exists."""

    def __init__(self, message: str = "User already exists", details: dict = None) -> None:
        super().__init__(message=message, status_code=409, error_code="USER_ALREADY_EXISTS", details=details)


class InvalidPasswordError(BaseCustomException):
    """Raised when password doesn't meet requirements."""

    def __init__(self, message: str = "Invalid password", details: dict = None) -> None:
        super().__init__(message=message, status_code=400, error_code="INVALID_PASSWORD", details=details)
