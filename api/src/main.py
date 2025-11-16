import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from src.core.config import settings
from src.core.exception_handlers import (
    custom_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from src.core.logging_config import setup_logging
from src.exceptions.base import BaseCustomException
from src.routes import auth
from src.routes.integrations import github

setup_logging()

app = FastAPI(
    title="TrackWise",
    description="A timeline-powered portfolio and progress tracker for visualizing career growth.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "layout": "BaseLayout",
        "filter": True,
        "tryItOutEnabled": True,
        "onComplete": "Ok",
    },
)


# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Middleware to log API hits with method, path, status, and duration."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start_time) * 1000  # ms

    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.2f}ms)")

    return response


app.add_exception_handler(BaseCustomException, custom_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth.router)
app.include_router(github.router)


@app.get("/")
def root() -> dict[str, Any]:
    logger.info("Home route accessed")
    return {"message": "FastAPI with PostgreSQL is running!", "port": settings.PORT}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=["127.0.0.1", "localhost"], port=settings.PORT, reload=True)
