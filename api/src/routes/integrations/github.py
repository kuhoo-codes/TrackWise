from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Errors
from src.db.database import get_db
from src.exceptions.external import GitHubIntegrationError
from src.repositories.integrations.external_profile_repository import ExternalProfileRepository
from src.repositories.integrations.github_repository import GithubRepository
from src.repositories.user_repository import UserRepository
from src.routes.timeline import get_timeline_service
from src.schemas.integrations.github import (
    GithubAuthUrlResponse,
    GithubSyncStatusResponse,
    OperationStatusEnum,
    OperationStatusResponse,
)
from src.services.auth_service import AuthService
from src.services.integrations.analysis.significance_analyzer_service import SignificanceAnalyzerService
from src.services.integrations.github_service import GithubService
from src.services.timeline_service import TimelineService

router = APIRouter(prefix="/integrations/github", tags=["GitHub Integration"])
security = HTTPBearer()


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    """Dependency to get AuthService with database session."""
    return AuthService(UserRepository(db))


def get_github_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
) -> GithubService:
    """
    Dependency to get GitHubService.
    It reuses get_timeline_service to ensure AI and Clustering are injected correctly.
    """
    return GithubService(
        repo=GithubRepository(db),
        external_profile_repo=ExternalProfileRepository(db),
        analyzer_service=SignificanceAnalyzerService(),
        timeline_service=timeline_service,
    )


@router.get("/auth-url")
async def get_github_auth_url(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> GithubAuthUrlResponse:
    """Generate GitHub OAuth URL"""
    token_data = auth_service.verify_token(token=credentials.credentials)
    auth_url = await github_service.get_auth_url(token_data.sub)
    return GithubAuthUrlResponse(authUrl=auth_url)


@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> Response:
    """Handle GitHub OAuth callback"""
    await github_service.handle_callback(code, state)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/sync")
async def start_github_sync(
    background_tasks: BackgroundTasks,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> OperationStatusResponse:
    """Start GitHub data synchronization in the background"""
    token_data = auth_service.verify_token(token=credentials.credentials)
    user_id = token_data.sub

    github_profile = await github_service.get_external_profile(user_id)
    access_token = await github_service.get_valid_access_token(github_profile)

    lock_acquired = await github_service.attempt_sync_lock(github_profile.id)

    if not lock_acquired:
        raise GitHubIntegrationError(
            Errors.GITHUB_INTEGRATION_ERROR.value,
            details={"message": "Another sync is already in progress for this profile."},
        )

    background_tasks.add_task(github_service.run_full_sync, access_token=access_token, github_profile=github_profile)
    return OperationStatusResponse(
        message="GitHub synchronization has been started.",
        status=OperationStatusEnum.accepted,
    )


@router.get("/sync-status")
async def get_github_sync_status(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> GithubSyncStatusResponse:
    """Get current GitHub sync status for the user"""
    token_data = auth_service.verify_token(token=credentials.credentials)
    user_id = token_data.sub

    return await github_service.get_sync_status(user_id)


@router.post("/sync-timelines", status_code=202)
async def sync_github_timelines(
    background_tasks: BackgroundTasks,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> JSONResponse:
    """
    Triggers the creation of timelines and nodes from all GitHub repositories of the user.
    """
    token_data = auth_service.verify_token(token=credentials.credentials)

    # We run this in the background to avoid timing out the HTTP request
    background_tasks.add_task(github_service.generate_all_github_timelines, token_data=token_data)
    return JSONResponse(
        status_code=202,
        content={"message": "Timeline generation for all repositories started in the background."},
    )
