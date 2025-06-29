from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.database import get_db
from src.repositories.user_repository import UserRepository
from src.schemas.users import Token, User, UserCreate, UserLogin
from src.services.auth_service import AuthService

router = APIRouter(tags=["Auth"], prefix="/auth")
security = HTTPBearer()


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    """Dependency to get AuthService with database session."""
    return AuthService(UserRepository(db))


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=Token)
async def signup(user: UserCreate, auth_service: Annotated[AuthService, Depends(get_auth_service)]) -> Token:
    """Sign up a new user."""
    user = await auth_service.create_user(user_data=user)
    access_token = auth_service.create_access_token(
        data={"sub": user.email},
    )
    return Token(access_token=access_token, token_type=settings.TOKEN_TYPE, user=User.model_validate(user))


@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login(
    user_credentials: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Login user and return access token."""
    user = await auth_service.authenticate_user(email=user_credentials.email, password=user_credentials.password)

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.email},
    )

    return Token(access_token=access_token, token_type=settings.TOKEN_TYPE, user=User.model_validate(user))


@router.get("/me", status_code=status.HTTP_200_OK, response_model=User)
async def get_user_data(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """Login user and return access token."""
    email = auth_service.verify_token(token=credentials.credentials)
    user = await auth_service.get_user_by_email(email=email)
    return User.model_validate(user)


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> JSONResponse:
    """Logout user by invalidating the token."""
    token = credentials.credentials
    await auth_service.add_to_blacklist(token)
