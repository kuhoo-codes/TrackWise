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


class Settings(BaseSettings):
    CLIENT_URL: str = os.getenv("CLIENT_URL")
    PORT: int = int(os.getenv("PORT", "8000"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET")
    GITHUB_CALLBACK_URL: str = "http://localhost:{PORT}/integration/github/callback"
    TOKEN_TYPE: str = os.getenv("TOKEN_TYPE", "Bearer")
    MINIMUM_PASSWORD_LENGTH: int = 8

    class Config:
        env_file = ".env"


settings = Settings()
