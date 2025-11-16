from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from redis.exceptions import ConnectionError

from src.core.config import Errors, settings
from src.core.redis_db import redis_client
from src.exceptions.auth import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.exceptions.external import ExternalServiceError
from src.models.users import User
from src.repositories.user_repository import UserRepository
from src.schemas.users import TokenData, UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token."""
        try:
            if self.is_token_blacklisted(token):
                raise TokenExpiredError(Errors.TOKEN_EXPIRED.value)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            email = payload.get("email")
            if user_id is None:
                raise InvalidTokenError(Errors.TOKEN_MISSING_PAYLOAD.value, details={"token_payload": payload})
            return TokenData(sub=user_id, email=email)
        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredError(Errors.TOKEN_EXPIRED.value) from e
        except JWTError as e:
            error_message = f"Invalid token: {e}"
            raise InvalidTokenError(error_message) from e

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsError(Errors.USER_ALREADY_EXISTS.value, details={"email": user_data.email})

        # Hash password and create user
        hashed_password = self.hash_password(user_data.password)
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        return await self.user_repo.create_user(db_user)

    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user and return access token."""
        # Get user by email
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise AuthenticationError(Errors.INVALID_EMAIL_OR_PASSWORD.value, details={"email": email})

        # Verify password
        if not self.verify_password(password, user.hashed_password):
            raise AuthenticationError(Errors.INVALID_EMAIL_OR_PASSWORD.value, details={"email": email})

        return user

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email."""
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise UserNotFoundError(Errors.USER_NOT_FOUND.value, details={"email": email})
        return user

    async def add_to_blacklist(self, token: str) -> None:
        """Add token to blacklist with TTL"""
        try:
            redis_client.set(token, "blacklisted", ex=self.access_token_expire_minutes * 60)
        except ConnectionError as e:
            raise ExternalServiceError(Errors.REDIS_CONNECTION_ERROR.value, details={"error": str(e)}) from e
        except Exception as e:
            raise ExternalServiceError(details={"error": str(e)}) from e

    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            return redis_client.exists(token) == 1
        except ConnectionError as e:
            raise ExternalServiceError(Errors.REDIS_CONNECTION_ERROR.value, details={"error": str(e)}) from e
        except Exception as e:
            raise ExternalServiceError(details={"error": str(e)}) from e
