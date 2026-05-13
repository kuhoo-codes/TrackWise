from typing import Annotated

from fastapi import APIRouter, Depends, File, Header, Response, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.database import get_db
from src.schemas.users import AvatarUpdateResponse, Token, User, UserCreate, UserLogin, UserUpdate
from src.services.auth_service import AuthService
from src.services.factory import ServiceFactory

router = APIRouter(tags=["Auth"], prefix="/auth")
security = HTTPBearer()


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    """Dependency to get AuthService with database session."""
    return ServiceFactory.create_auth_service(db)


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=Token)
async def signup(user: UserCreate, auth_service: Annotated[AuthService, Depends(get_auth_service)]) -> Token:
    """Sign up a new user."""
    user = await auth_service.create_user(user_data=user)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email},
    )
    return Token(access_token=access_token, token_type=settings.TOKEN_TYPE, user=User.model_validate(user))


@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login(
    user_credentials: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Login user and return access token."""
    user = await auth_service.authenticate_user(email=user_credentials.email, password=user_credentials.password)

    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email},
    )

    return Token(access_token=access_token, token_type=settings.TOKEN_TYPE, user=User.model_validate(user))


@router.get("/me", status_code=status.HTTP_200_OK, response_model=User)
async def get_user_data(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """Login user and return access token."""
    token_data = auth_service.verify_token(token=credentials.credentials)
    user = await auth_service.get_user_by_email(email=token_data.email)
    return User.model_validate(user)


@router.patch("/me", status_code=status.HTTP_200_OK, response_model=User)
async def update_user(
    update_data: UserUpdate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """Updates the current user's name and headline."""
    token_data = auth_service.verify_token(token=credentials.credentials)

    updated_user = await auth_service.update_user(user_id=token_data.sub, profile_data=update_data)

    return User.model_validate(updated_user)


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> JSONResponse:
    """Logout user by invalidating the token."""
    token = credentials.credentials
    await auth_service.add_to_blacklist(token=token)


@router.patch("/me/avatar", status_code=status.HTTP_200_OK, response_model=AvatarUpdateResponse)
async def upload_avatar(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    file: Annotated[UploadFile, File()],
) -> AvatarUpdateResponse:
    """
    Uploads and stores an avatar image as binary data in the database.
    Only allows image MIME types.
    """
    token_data = auth_service.verify_token(token=credentials.credentials)
    user_id = token_data.sub
    await auth_service.update_avatar(user_id=user_id, file=file)

    return AvatarUpdateResponse(
        message="Avatar updated successfully", has_avatar=True, avatar_url=f"/auth/users/avatar/{user_id}"
    )


@router.get("/me/avatar", status_code=status.HTTP_200_OK)
async def get_avatar(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    if_none_match: Annotated[str | None, Header()] = None,
) -> Response:
    """
    Serves avatar with ETag validation using DB timestamps.
    Prevents binary transfer if the browser's cache is current.
    """
    # 1. Get metadata only (Fast DB hit)

    token_data = auth_service.verify_token(token=credentials.credentials)
    user_id = token_data.sub
    metadata = await auth_service.get_avatar_info(user_id=user_id)
    logger.error(f"Received If-None-Match: {if_none_match} from client")

    if not metadata:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    updated_at, media_type = metadata

    # 2. Generate Weak ETag based on unix timestamp
    etag = f'W/"{int(updated_at.timestamp())}"'

    logger.error(f"Generated ETag: {etag} for user_id: {user_id} with updated_at: {updated_at}")

    # 3. Check for Cache Hit (Return 304 - No Body)
    if if_none_match == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    # 4. Cache Miss - Get the heavy bytes
    avatar_blob = await auth_service.get_avatar_bytes(user_id=user_id)
    if not avatar_blob:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    # 5. Return Full Image
    return Response(
        content=avatar_blob,
        media_type=media_type,
        headers={
            "ETag": etag,
            "Cache-Control": "public, max-age=31536000",  # 1 year
        },
    )


@router.delete("/me/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def remove_avatar(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """Removes the user's avatar and resets to default initials."""
    token_data = auth_service.verify_token(token=credentials.credentials)
    user_id = token_data.sub

    await auth_service.remove_avatar(user_id=user_id)
