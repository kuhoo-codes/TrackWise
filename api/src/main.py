from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
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

app.include_router(auth.router)
app.include_router(github.router)


@app.get("/")
def root() -> dict[str, Any]:
    return {"message": "FastAPI with PostgreSQL is running!", "port": settings.PORT}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=["127.0.0.1", "localhost"], port=settings.PORT, reload=True)
