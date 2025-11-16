from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.exceptions.external import GitHubIntegrationError
from src.models.integrations import ExternalProfile, PlatformEnum
from src.schemas.integrations.github import GithubToken


@pytest.fixture
def mock_github_repo() -> AsyncMock:
    """Fixture for a mocked GitHubRepository."""
    return AsyncMock()


@pytest.fixture
def mock_external_profile_repo() -> AsyncMock:
    """Fixture for a mocked ExternalProfileRepository."""
    return AsyncMock()


@pytest.fixture
def github_service(mock_github_repo: AsyncMock, mock_external_profile_repo: AsyncMock) -> GithubService:
    """Fixture for the GitHubService with a mocked repository."""
    return GitHubService(repo=mock_github_repo)


# --- Tests for get_auth_url ---


@pytest.mark.asyncio
@patch("src.services.integrations.github_service.secrets.token_urlsafe")
async def test_get_auth_url(
    mock_token_urlsafe: MagicMock, github_service: GithubService, mock_github_repo: AsyncMock
) -> None:
    """
    Test that get_auth_url generates a correct URL and saves the state.
    """
    # --- Setup ---
    mock_token_urlsafe.return_value = "test_state_token"
    user_id = "user-123"

    # --- Execute ---
    auth_url = await github_service.get_auth_url(user_id)

    # --- Assert ---
    mock_github_repo.save_state.assert_called_once_with("test_state_token", user_id)

    assert "https://github.com/login/oauth/authorize" in auth_url
    assert "client_id=" in auth_url
    assert "state=test_state_token" in auth_url


# --- Tests for handle_callback ---


@pytest.mark.asyncio
async def test_handle_callback_success(github_service: GithubService, mock_github_repo: AsyncMock) -> None:
    """
    Test the successful handling of a GitHub OAuth callback.
    """
    # --- Setup ---
    code = "test_code"
    state = "test_state"
    user_id = "user-123"

    # Mock the repository calls.
    mock_state_record = AsyncMock()
    mock_state_record.user_id = user_id
    mock_github_repo.validate_state.return_value = mock_state_record

    mock_saved_token = AsyncMock()
    mock_saved_token.access_token = "gh_token_123"
    mock_saved_token.token_type = "bearer"
    mock_github_repo.save_token.return_value = mock_saved_token

    token_data = GithubToken(
        access_token="gh_token_123",
        token_type="bearer",
        scope="",
        refresh_token="gh_refresh_123",
        expires_in=60,
        refresh_token_expires_in=60,
        created_at=datetime.now(),
    )
    with patch.object(github_service, "exchange_github_code", return_value=token_data) as mock_exchange:
        # --- Execute ---
        result = await github_service.handle_callback(code, state)

        # --- Assert ---
        mock_github_repo.validate_state.assert_called_once_with(state)
        mock_exchange.assert_called_once()
        mock_github_repo.save_token.assert_called_once_with(user_id, token_data)

        assert isinstance(result, TokenResponse)
        assert result.access_token == "gh_token_123"


# --- Tests for exchange_github_code ---


@pytest.mark.asyncio
@patch("src.services.integrations.github_service.httpx.AsyncClient")
async def test_exchange_github_code_success(mock_async_client: MagicMock, github_service: GithubService) -> None:
    """
    Test the successful exchange of an OAuth code for a GitHub token.
    """
    # --- Setup ---
    mock_data = {
        "access_token": "gh_token_123",
        "token_type": "bearer",
        "scope": "repo,user",
        "refresh_token": "gh_refresh_123",
        "expires_in": 60,
        "refresh_token_expires_in": 60,
        "created_at": datetime.now(),
    }

    mock_response = MagicMock()
    mock_response.json.return_value = mock_data

    mock_async_client.return_value.__aenter__.return_value.post.return_value = mock_response

    # --- Execute ---
    result = await github_service.exchange_github_code("test_code", "test_client_id", "test_client_secret")

    # --- Assert ---
    assert isinstance(result, GithubToken)
    assert result.access_token == mock_data["access_token"]
    assert result.token_type == mock_data["token_type"]
    assert result.scope == mock_data["scope"]
    assert result.refresh_token == mock_data["refresh_token"]
    assert result.expires_in == mock_data["expires_in"]
    assert result.refresh_token_expires_in == mock_data["refresh_token_expires_in"]
    assert result.created_at == mock_data["created_at"]


@pytest.mark.asyncio
@patch("src.services.integrations.github_service.httpx.AsyncClient")
async def test_exchange_github_code_failure(mock_async_client: MagicMock, github_service: GithubService) -> None:
    """
    Test the handling of a failed OAuth code exchange.
    """
    # --- Setup ---
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "error": "bad_verification_code",
        "error_description": "The code passed is incorrect or expired.",
        "error_uri": "https://docs.github.com/apps/managing-oauth-apps/troubleshooting-oauth-app-access-token-request-errors/",
    }
    mock_async_client.return_value.__aenter__.return_value.post.return_value = mock_response

    # --- Execute ---
    with pytest.raises(GitHubIntegrationError) as exc_info:
        await github_service.exchange_github_code("bad_code", "test_client_id", "test_client_secret")

    # --- Assert ---
    assert "GitHub integration error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_external_profile(github_service: GithubService, mock_external_profile_repo: AsyncMock) -> None:
    """Test that create_external_profile correctly builds and saves a new ExternalProfile."""
    github_user = User(
        id=123,
        login="octocat",
        name="The Octocat",
        avatar_url="avatar",
        html_url="profile",
        repos_url="https://api.github.com/users/octocat/repos",
        events_url="https://api.github.com/users/octocat/events",
        type="User",
        email="octocat@example.com",
    )

    github_token = GithubToken(
        access_token="new_token",
        refresh_token="new_refresh",
        access_token_expires_at=datetime.now(timezone.utc),
        refresh_token_expires_at=datetime.now(timezone.utc),
        token_type="bearer",
        expires_in=3600,
        refresh_token_expires_in=7200,
    )
    mock_external_profile_repo.create_external_profile.return_value = "created_profile"

    result = await github_service.create_external_profile(github_user, 42, github_token)

    mock_external_profile_repo.create_external_profile.assert_called_once()
    assert result == "created_profile"
