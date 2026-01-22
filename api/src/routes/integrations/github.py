from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Errors
from src.db.database import get_db
from src.exceptions.auth import UserNotFoundError
from src.repositories.integrations.external_profile_repository import ExternalProfileRepository
from src.repositories.integrations.github_repository import GithubRepository
from src.repositories.user_repository import UserRepository
from src.schemas.integrations.github import TokenResponse
from src.services.auth_service import AuthService
from src.services.integrations.github_service import GithubService
from src.services.integrations.significance_analyzer_service import SignificanceAnalyzerService

router = APIRouter(prefix="/integrations/github", tags=["GitHub Integration"])
security = HTTPBearer()


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    """Dependency to get AuthService with database session."""
    return AuthService(UserRepository(db))


def get_github_service(db: Annotated[AsyncSession, Depends(get_db)]) -> GithubService:
    """Dependency to get GitHubService with database session."""
    return GithubService(GithubRepository(db), ExternalProfileRepository(db), SignificanceAnalyzerService())


@router.get("/auth-url")
async def get_github_auth_url(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> JSONResponse:
    """Generate GitHub OAuth URL"""
    token_data = auth_service.verify_token(token=credentials.credentials)
    auth_url = await github_service.get_auth_url(token_data.sub)
    return JSONResponse(content={"authUrl": auth_url})


@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> TokenResponse:
    """Handle GitHub OAuth callback"""
    return await github_service.handle_callback(code, state)


@router.get("/sync")
async def start_github_sync(
    background_tasks: BackgroundTasks,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> JSONResponse:
    """Start GitHub data synchronization in the background"""
    token_data = auth_service.verify_token(token=credentials.credentials)
    user_id = token_data.sub

    access_token, github_profile = await github_service.get_valid_access_token(user_id)

    if not github_profile:
        raise UserNotFoundError(Errors.USER_NOT_FOUND.value, details={"error": "GitHub external profile not found"})

    background_tasks.add_task(github_service.run_full_sync, access_token=access_token, github_profile=github_profile)
    return JSONResponse(
        status_code=200,
        content={"message": "GitHub synchronization has been started."},
    )
