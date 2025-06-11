import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


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

    class Config:
        env_file = ".env"


settings = Settings()
