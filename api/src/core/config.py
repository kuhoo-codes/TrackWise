import os
from enum import Enum

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


class Errors(str, Enum):
    USER_ALREADY_EXISTS: str = "User with this email already exists"
    USER_NOT_FOUND: str = "User not found"
    INVALID_EMAIL_OR_PASSWORD: str = "Invalid email or password"  # noqa: S105
    TOKEN_EXPIRED: str = "Token has expired"  # noqa: S105
    TOKEN_MISSING_PAYLOAD: str = "Token payload missing subject"  # noqa: S105
    PASSWORD_MUST_CONTAIN_SPECIAL_CHARACTER: str = "Password must contain at least one special character"  # noqa: S105
    GITHUB_INTEGRATION_ERROR: str = "GitHub integration error"
    REDIS_CONNECTION_ERROR: str = "Failed to connect to Redis"
    TIMELINE_NOT_FOUND: str = "Timeline not found"
    TIMELINE_NODE_NOT_FOUND: str = "Timeline node not found"
    INVALID_TIMELINE_NODE_HIERARCHY: str = "Invalid timeline node hierarchy"
    INVALID_TIMELINE_NODE: str = "Invalid timeline node data"


class GithubRoutes(str, Enum):
    REPOSITORIES: str = "repos"
    ISSUES: str = "issues"
    USER: str = "user"
    USERS: str = "users"
    COMMITS: str = "commits"


class Settings(BaseSettings):
    CLIENT_URL: str = os.getenv("CLIENT_URL", "http://localhost:5173/")
    PORT: int = int(os.getenv("PORT", "8000"))
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://username:password@localhost:5432/database_name")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_CALLBACK_URL: str = "http://localhost:{PORT}/integration/github/callback"
    GITHUB_BASE_API_URL: str = "https://api.github.com"
    GITHUB_PER_PAGE: int = 100
    TOKEN_TYPE: str = os.getenv("TOKEN_TYPE", "Bearer")
    MINIMUM_PASSWORD_LENGTH: int = 8

    class Config:
        env_file = ".env"


settings = Settings()
