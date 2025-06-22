from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import settings
from src.core.exception_handlers import (
    custom_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from src.exceptions.base import BaseCustomException
from src.routes import auth
from src.routes.integrations import github

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

app.add_exception_handler(BaseCustomException, custom_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth.router)
app.include_router(github.router)


@app.get("/")
def root() -> dict[str, Any]:
    return {"message": "FastAPI with PostgreSQL is running!", "port": settings.PORT}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=["127.0.0.1", "localhost"], port=settings.PORT, reload=True)
