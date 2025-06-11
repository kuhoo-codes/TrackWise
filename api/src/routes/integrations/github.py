from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from src.dependencies.auth import get_current_user
from src.repositories.github_repo import GitHubRepository
from src.schemas.integrations.github import TokenData, TokenResponse
from src.services.integrations.github_service import GitHubService

router = APIRouter(prefix="/integrations/github", tags=["GitHub Integration"])
security = HTTPBearer()
github_service = GitHubService(GitHubRepository())


@router.get("/auth-url")
async def get_github_auth_url(token_data: Annotated[TokenData, Depends(get_current_user)]) -> JSONResponse:
    """Generate GitHub OAuth URL"""
    auth_url = await github_service.get_auth_url(token_data.user_id)
    return JSONResponse(content={"authUrl": auth_url})


@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
) -> TokenResponse:
    """Handle GitHub OAuth callback"""
    return await github_service.handle_callback(code, state)
