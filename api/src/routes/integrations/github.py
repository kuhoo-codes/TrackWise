from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Errors
from src.db.database import get_db
from src.exceptions.external import GitHubIntegrationError
from src.routes.auth import get_auth_service
from src.schemas.integrations.github import (
    GithubAuthUrlResponse,
    GithubSyncStatusResponse,
    OperationStatusEnum,
    OperationStatusResponse,
    RepositoryInDB,
)
from src.services.auth_service import AuthService
from src.services.factory import ServiceFactory
from src.services.integrations.github_service import GithubService
from src.services.timeline_service import TimelineService

router = APIRouter(prefix="/integrations/github", tags=["GitHub Integration"])
security = HTTPBearer()


def get_github_service(db: Annotated[AsyncSession, Depends(get_db)]) -> GithubService:
    """
    Dependency to get GitHubService.
    """
    return ServiceFactory.create_github_service(db)


@router.get("/auth-url")
async def get_github_auth_url(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> GithubAuthUrlResponse:
    """Generate GitHub OAuth URL"""
    token_data = auth_service.verify_token(token=credentials.credentials)
    auth_url = await github_service.get_auth_url(user_id=token_data.sub)
    return GithubAuthUrlResponse(authUrl=auth_url)


@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> Response:
    """Handle GitHub OAuth callback"""
    await github_service.handle_callback(code=code, state=state)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/repositories")
async def get_github_repositories(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> list[RepositoryInDB]:
    """Get all GitHub repositories for the user"""
    token_data = auth_service.verify_token(token=credentials.credentials)
    user_id = token_data.sub
    return await github_service.get_all_repositories(user_id=user_id)


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

    github_profile = await github_service.get_external_profile(user_id=user_id)
    access_token = await github_service.get_valid_access_token(github_profile=github_profile)

    lock_acquired = await github_service.attempt_sync_lock(profile_id=github_profile.id)

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

    return await github_service.get_sync_status(user_id=user_id)


@router.post("/timelines", status_code=202)
async def sync_github_timelines(
    repository_ids: list[int],
    background_tasks: BackgroundTasks,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> OperationStatusResponse:
    """
    Triggers the creation of timelines and nodes from all GitHub repositories of the user.
    """
    token_data = auth_service.verify_token(token=credentials.credentials)
    locked_repo_ids = await github_service.repo.lock_repos_for_timeline_generation(repo_ids=repository_ids)

    if not locked_repo_ids:
        return OperationStatusResponse(
            message="All selected repositories are currently being processed.",
            status=OperationStatusEnum.queued,
        )

    background_tasks.add_task(
        github_service.generate_github_timelines, token_data=token_data, repository_ids=locked_repo_ids
    )
    return OperationStatusResponse(
        message="Timeline generation for all repositories started in the background.",
        status=OperationStatusEnum.accepted,
    )


@router.delete("", status_code=status.HTTP_200_OK)
async def disconnect_github(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    github_service: Annotated[GithubService, Depends(get_github_service)],
) -> OperationStatusResponse:
    """Disconnect GitHub account and remove all related data"""
    token_data = auth_service.verify_token(token=credentials.credentials)
    user_id = token_data.sub
    await github_service.disconnect_github(user_id=user_id)
    return OperationStatusResponse(
        message="GitHub account disconnected successfully.",
        status=OperationStatusEnum.completed,
    )
