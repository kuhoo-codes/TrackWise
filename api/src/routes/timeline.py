from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.database import get_db
from src.models.timelines import Timeline
from src.repositories.timeline_repository import TimelineRepository
from src.repositories.user_repository import UserRepository
from src.schemas.timelines import Timeline as TimelineSchema
from src.schemas.timelines import (
    TimelineCreate,
    TimelineNode,
    TimelineNodeBase,
    TimelineNodeCreate,
    TimelineNodeWithChildren,
    TimelineSummary,
)
from src.services.auth_service import AuthService
from src.services.integrations.ai.providers.gemini_provider import GeminiProvider
from src.services.integrations.ai.providers.ollama_provider import OllamaProvider
from src.services.integrations.ai.timeline_analysis_service import TimelineAnalysisService
from src.services.integrations.analysis.activity_clustering_service import ActivityClusteringService
from src.services.timeline_service import TimelineService

router = APIRouter(tags=["Timeline"], prefix="/timelines")
security = HTTPBearer()


def get_timeline_service(db: Annotated[AsyncSession, Depends(get_db)]) -> TimelineService:
    """Dependency to get TimelineService with all required sub-services."""

    # 1. Initialize Repository
    repo = TimelineRepository(db)

    # 2. Initialize Clustering Logic (Phase 2)
    clustering = ActivityClusteringService()

    # 3. Initialize AI Provider (Phase 3)
    # Switch this to GeminiProvider(settings.GEMINI_API_KEY) for production
    if settings.ENVIRONMENT == "development":
        ai_provider = OllamaProvider()
    else:
        ai_provider = GeminiProvider(api_key=settings.GEMINI_API_KEY)

    ai_service = TimelineAnalysisService(provider=ai_provider)

    # 4. Return the fully composed Service
    return TimelineService(timeline_repo=repo, clustering_service=clustering, ai_service=ai_service)


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    """Dependency to get AuthService with database session."""
    return AuthService(UserRepository(db))


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[TimelineSummary])
async def get_timelines(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> list[TimelineSummary]:
    """
    Get ALL timelines for the authenticated user.
    """
    token_data = auth_service.verify_token(token=credentials.credentials)
    return await timeline_service.get_user_timelines(token_data.sub)


@router.get("/{timeline_id}", status_code=status.HTTP_200_OK, response_model=TimelineSchema)
async def get_timeline(
    timeline_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Timeline:
    """Get timeline for the authenticated user."""
    token_data = auth_service.verify_token(token=credentials.credentials)
    return await timeline_service.get_timeline_details(timeline_id, token_data.sub)


@router.delete("/{timeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline(
    timeline_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """Delete timeline for the authenticated user."""
    token_data = auth_service.verify_token(token=credentials.credentials)
    await timeline_service.delete_timeline(timeline_id, token_data.sub)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TimelineSchema)
async def create_timeline(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    timeline: TimelineCreate,
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Timeline:
    """Create a new timeline."""
    token_data = auth_service.verify_token(token=credentials.credentials)
    return await timeline_service.create_timeline(timeline, token_data)


@router.get("/node/{node_id}", status_code=status.HTTP_200_OK, response_model=TimelineNodeWithChildren)
async def get_timeline_node(
    node_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TimelineNodeWithChildren:
    """Get a timeline node by ID."""
    auth_service.verify_token(token=credentials.credentials)
    return await timeline_service.get_timeline_node_by_id(node_id)


@router.post("/node", status_code=status.HTTP_201_CREATED, response_model=TimelineNode)
async def create_timeline_node(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    timeline_node: TimelineNodeCreate,
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TimelineNode:
    """Create a new timeline node."""
    token_data = auth_service.verify_token(token=credentials.credentials)
    return await timeline_service.create_timeline_node(timeline_node, token_data.sub)


@router.patch("/node/{node_id}", status_code=status.HTTP_200_OK, response_model=TimelineNode)
async def update_timeline_node(
    node_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    timeline_node: TimelineNodeBase,
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TimelineNode:
    """Update a timeline node."""
    token_data = auth_service.verify_token(token=credentials.credentials)
    return await timeline_service.update_timeline_node(node_id, timeline_node, token_data.sub)


@router.delete("/node/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline_node(
    node_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    timeline_service: Annotated[TimelineService, Depends(get_timeline_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """Delete a timeline node."""
    token_data = auth_service.verify_token(token=credentials.credentials)
    await timeline_service.delete_timeline_node(node_id, token_data.sub)
