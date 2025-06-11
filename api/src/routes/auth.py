from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.database import get_db
from src.repositories.user_repository import UserRepository
from src.schemas.users import Token, UserCreate, UserLogin
from src.services.auth_service import AuthService

router = APIRouter(tags=["Auth"], prefix="/auth")


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    """Dependency to get AuthService with database session."""
    return AuthService(UserRepository(db))


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=Token)
async def signup(user: UserCreate, auth_service: Annotated[AuthService, Depends(get_auth_service)]) -> Token:
    """Sign up a new user."""
    user = auth_service.create_user(user_data=user)
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "user_id": user.id, "user_name": user.name},
    )
    return Token(access_token=access_token, token_type=settings.TOKEN_TYPE)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login(
    user_credentials: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Login user and return access token."""
    return auth_service.authenticate_user(email=user_credentials.email, password=user_credentials.password)
