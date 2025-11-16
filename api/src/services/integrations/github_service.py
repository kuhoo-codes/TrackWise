import secrets
from datetime import datetime, timezone
from typing import Annotated

import httpx
from pydantic import TypeAdapter

from src.core.config import Errors, settings
from src.exceptions.external import GitHubIntegrationError
from src.repositories.integrations.external_profile_repository import ExternalProfileRepository
from src.schemas.integrations.github import GitHubToken, GitHubTokenError, TokenResponse


class GithubService:
    def __init__(self, repo: GithubRepository, external_profile_repo: ExternalProfileRepository) -> None:
        self.repo = repo
        self.external_profile_repo = external_profile_repo

    async def get_auth_url(self, user_id: Annotated[str, "Associated user ID"]) -> str:
        """Generate GitHub OAuth authorization URL."""
        state = secrets.token_urlsafe(16)
        await self.repo.save_state(state, user_id)

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "state": state,
        }
        return f"https://github.com/login/oauth/authorize?{httpx.QueryParams(params)}"

    async def handle_callback(self, code: str, state: Annotated[str, "GitHub OAuth state parameter"]) -> TokenResponse:
        """Handle GitHub OAuth callback and exchange code for token."""
        state_record = await self.repo.validate_state(state)
        user_id = state_record.user_id
        github_token = await self.exchange_github_code(
            code=code, client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_CLIENT_SECRET
        )
        await self.repo.save_token(user_id, github_token)
        external_profile = await self.external_profile_repo.get_external_profile_by_user_id(
            user_id, PlatformEnum.GITHUB
        )
        if external_profile:
            await self.update_external_profile_token(external_profile, github_token)
        else:
            github_user = await self.get_auth_user(github_token.access_token)
            await self.create_external_profile(github_user, user_id, github_token)
        return TokenResponse(access_token=github_token.access_token, token_type=github_token.token_type)

    async def exchange_github_code(self, code: str, client_id: str, client_secret: str) -> GithubToken:
        """Handle GitHub OAuth code exchange"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                json={"client_id": client_id, "client_secret": client_secret, "code": code},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        if "error" in data:
            raise GitHubIntegrationError(
                Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": data.get("error_description")}
            )

        return GithubToken(**data)

    async def create_external_profile(
        self, github_user: User, user_id: int, github_token: GithubToken
    ) -> ExternalProfile:
        """Create a new ExternalProfile for the user."""
        external_profile = ExternalProfile(
            external_id=github_user.id,
            user_id=user_id,
            platform=PlatformEnum.GITHUB,
            external_username=github_user.login,
            access_token=github_token.access_token,
            refresh_token=github_token.refresh_token,
            access_token_expires_at=github_token.access_token_expires_at,
            refresh_token_expires_at=github_token.refresh_token_expires_at,
            last_synced_at=None,
        )

        return await self.external_profile_repo.create_external_profile(external_profile)

