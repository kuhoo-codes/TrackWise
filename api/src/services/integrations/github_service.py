import secrets

import httpx

from src.core.config import Errors, settings
from src.exceptions.external import GitHubIntegrationError
from src.repositories.github_repo import GitHubRepository
from src.schemas.integrations.github import GitHubToken, GitHubTokenError, TokenResponse


class GitHubService:
    def __init__(self, repo: GitHubRepository) -> None:
        self.repo = repo

    async def get_auth_url(self, user_id: str) -> str:
        state = secrets.token_urlsafe(16)
        await self.repo.save_state(state, user_id)

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "state": state,
        }
        return f"https://github.com/login/oauth/authorize?{httpx.QueryParams(params)}"

    async def handle_callback(self, code: str, state: str) -> TokenResponse:
        state_record = await self.repo.validate_state(state)
        user_id = state_record.user_id
        token_data = await self.exchange_github_code(
            code=code, client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_CLIENT_SECRET
        )
        github_token = await self.repo.save_token(user_id, token_data)

        return TokenResponse(access_token=github_token.access_token, token_type=github_token.token_type)

    async def exchange_github_code(self, code: str, client_id: str, client_secret: str) -> GitHubToken:
        """Handle GitHub OAuth code exchange"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                json={"client_id": client_id, "client_secret": client_secret, "code": code},
                headers={"Accept": "application/json"},
            )
        token_response: GitHubToken | GitHubTokenError = response.json()
        if "error" in token_response:
            token_response = GitHubTokenError(**token_response)
            raise GitHubIntegrationError(
                Errors.GITHUB_INTEGRATION_ERROR.value,
                details={"error": token_response.error_description},
            )
        return token_response
