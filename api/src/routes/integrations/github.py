from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.repositories.github_repo import GitHubRepository
from src.repositories.user_repository import UserRepository
from src.schemas.integrations.github import TokenResponse
from src.services.auth_service import AuthService
from src.services.integrations.github_service import GitHubService

router = APIRouter(prefix="/integrations/github", tags=["GitHub Integration"])
security = HTTPBearer()
github_service = GitHubService(GitHubRepository())


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    """Dependency to get AuthService with database session."""
    return AuthService(UserRepository(db))


@router.get("/auth-url")
async def get_github_auth_url(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> JSONResponse:
    """Generate GitHub OAuth URL"""
    user_id = auth_service.verify_token(token=credentials.credentials)
    auth_url = await github_service.get_auth_url(user_id)
    return JSONResponse(content={"authUrl": auth_url})


@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
) -> TokenResponse:
    """Handle GitHub OAuth callback"""
    return await github_service.handle_callback(code, state)
