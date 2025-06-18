import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from src.core.config import settings
from src.schemas.base import TimestampSchema


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < settings.MINIMUM_PASSWORD_LENGTH:
            raise Exception()
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise Exception()
        return v


class User(UserBase, TimestampSchema):
    id: int
    last_login: datetime


class UserInDB(User):
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User | None = None
