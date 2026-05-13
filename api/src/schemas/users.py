import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

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
    headline: str | None = None
    has_avatar: bool = False

    @model_validator(mode="before")
    @classmethod
    def check_avatar_exists(cls, data: object) -> object:
        if hasattr(data, "media_type"):
            data.has_avatar = data.media_type is not None
        return data


class UserInDB(User):
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    headline: str | None = Field(None, max_length=150)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Ensure name isn't just whitespace
        if not v.strip():
            msg = "Name cannot be empty or only whitespace"
            raise ValidationError(msg, details={"field": "name", "reason": "whitespace_only"})
        # Prevent specific characters if needed
        if re.search(r"[<>{}[\]\\]", v):
            msg = "Name contains invalid characters"
            raise ValidationError(msg, details={"field": "name", "reason": "invalid_characters"})
        return v.strip()

    @field_validator("headline")
    @classmethod
    def validate_headline(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Headlines can be empty strings, but not just spaces
        if v != "" and not v.strip():
            msg = "Headline cannot be only whitespace"
            raise ValidationError(msg, details={"field": "headline", "reason": "whitespace_only"})
        return v.strip()


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User | None = None


class TokenData(BaseModel):
    sub: int
    email: str


class AvatarUpdateResponse(BaseModel):
    message: str
    has_avatar: bool
    avatar_url: str
