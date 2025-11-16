from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from src.exceptions.base import BaseCustomException


class ErrorResponse:
    """Standardized error response format."""

    @staticmethod
    def create_error_response(error_code: str, message: str, details: dict[str, Any] = None) -> dict[str, Any]:
        """Create standardized error response."""
        response = {
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": datetime.now().isoformat() + "Z",
            }
        }

        if details:
            response["error"]["details"] = details

        return response


async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """Handle custom exceptions."""
    logger.error(f"Custom exception occurred: {exc.message} | Details: {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.error(f"HTTP exception occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.create_error_response(
            error_code="HTTP_ERROR",
            message=str(exc.detail),
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({"field": field_path, "message": error["msg"], "type": error["type"]})

    logger.error(f"Validation exception occurred: {errors}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse.create_error_response(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            details={"validation_errors": errors},
        ),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    logger.error(f"Database exception occurred: {str(exc)}")
    # Don't expose internal database errors to users
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.create_error_response(
            error_code="DATABASE_ERROR",
            message="An internal database error occurred",
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected exception occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.create_error_response(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
        ),
    )
