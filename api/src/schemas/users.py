import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from src.core.config import Errors, settings
from src.exceptions.validation import ValidationError
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
            error_message = f"Password must be at least {settings.MINIMUM_PASSWORD_LENGTH} characters long"
            raise ValidationError(
                error_message, details={"field": "password", "min_length": settings.MINIMUM_PASSWORD_LENGTH}
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValidationError(
                Errors.PASSWORD_MUST_CONTAIN_SPECIAL_CHARACTER.value,
                details={"field": "password", "requirement": "special_character"},
            )
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
