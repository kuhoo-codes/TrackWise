from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.exceptions.external import GitHubIntegrationError
from src.models.integrations import ExternalProfile, PlatformEnum
from src.schemas.integrations.github import GithubToken, RepoCommit, TokenResponse, User
from src.services.integrations.github_service import GithubService


@pytest.fixture
def mock_github_repo() -> AsyncMock:
    """Fixture for a mocked GitHubRepository."""
    return AsyncMock()


@pytest.fixture
def mock_external_profile_repo() -> AsyncMock:
    """Fixture for a mocked ExternalProfileRepository."""
    return AsyncMock()


@pytest.fixture
def mock_significance_service() -> MagicMock:
    """Fixture for a mocked SignificanceAnalyzerService."""
    return MagicMock()


@pytest.fixture
def mock_timeline_service() -> AsyncMock:
    """Fixture for a mocked TimelineService."""
    return AsyncMock()


@pytest.fixture
def github_service(
    mock_github_repo: AsyncMock,
    mock_external_profile_repo: AsyncMock,
    mock_significance_service: MagicMock,
    mock_timeline_service: AsyncMock,
) -> GithubService:
    return GithubService(
        repo=mock_github_repo,
        external_profile_repo=mock_external_profile_repo,
        analyzer_service=mock_significance_service,
        timeline_service=mock_timeline_service,
    )


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


@pytest.mark.asyncio
async def test_update_external_profile_token(
    github_service: GithubService, mock_external_profile_repo: AsyncMock
) -> None:
    """Test that update_external_profile_token updates and saves tokens."""
    token = GithubToken(
        access_token="new_token",
        refresh_token="new_refresh",
        access_token_expires_at=datetime.now(timezone.utc),
        refresh_token_expires_at=datetime.now(timezone.utc),
        token_type="bearer",
        expires_in=3600,
        refresh_token_expires_in=7200,
    )
    external_profile = ExternalProfile(id=1, user_id=1, platform=PlatformEnum.GITHUB)
    mock_external_profile_repo.update_external_profile.return_value = "updated_profile"

    result = await github_service.update_external_profile_token(external_profile, token)

    mock_external_profile_repo.update_external_profile.assert_called_once_with(external_profile)
    assert external_profile.access_token == "new_token"
    assert result == "updated_profile"


@pytest.mark.asyncio
@patch("src.services.integrations.github_service.httpx.AsyncClient")
async def test_get_auth_user_success(mock_client: MagicMock, github_service: GithubService) -> None:
    """Test fetching authenticated GitHub user."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 1,
        "login": "octocat",
        "name": "The Octocat",
        "avatar_url": "avatar",
        "html_url": "url",
        "repos_url": "repos",
        "events_url": "events",
        "type": "User",
        "email": "octo@example.com",
    }
    mock_response.raise_for_status.return_value = None
    mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

    user = await github_service.get_auth_user("token")

    assert user.login == "octocat"
    assert user.id == 1


@patch("src.services.integrations.github_service.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_fetch_author_commits_for_repo(mock_client: MagicMock, github_service: GithubService) -> None:
    now = datetime.now()

    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "sha": "abc",
            "url": "url1",
            "html_url": "https://github.com/user/repo/commit/abc",
            "commit": {
                "message": "Initial commit",
                "author": {"name": "octocat", "email": "octocat@example.com", "date": "2025-11-13T00:00:00Z"},
            },
        },
        {
            "sha": "def",
            "url": "url2",
            "html_url": "https://github.com/user/repo/commit/def",
            "commit": {
                "message": "Fix bug",
                "author": {"name": "octocat", "email": "octocat@example.com", "date": "2025-11-13T00:00:00Z"},
            },
        },
    ]

    mock_response.headers = {}
    mock_response.raise_for_status.return_value = None

    # ✅ create async instance and async mock
    async_client_instance = mock_client.return_value.__aenter__.return_value
    async_client_instance.get = AsyncMock(return_value=mock_response)

    # ✅ pass the instance, not the class mock
    commits = await github_service.fetch_author_commits_for_repo(async_client_instance, "user/repo", "octocat", now)

    assert len(commits) == 2


@pytest.mark.asyncio
@patch("src.services.integrations.github_service.httpx.AsyncClient")
async def test_get_valid_access_token_refresh_success(
    mock_client: MagicMock, github_service: GithubService, mock_external_profile_repo: AsyncMock
) -> None:
    """Test refreshing an expired access token using refresh token."""
    valid_refresh = datetime.now(timezone.utc) + timedelta(days=1)
    external_profile = ExternalProfile(
        user_id=1,
        refresh_token="refresh123",
        refresh_token_expires_at=valid_refresh,
        platform=PlatformEnum.GITHUB,
    )

    mock_external_profile_repo.get_external_profile_by_user_id.return_value = external_profile
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "access_token": "new_access",
        "refresh_token": "new_refresh",
        "token_type": "bearer",
        "scope": "repo",
        "expires_in": 3600,
        "refresh_token_expires_in": 2592000,
    }
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
    mock_external_profile_repo.update_external_profile.return_value = external_profile

    token, profile = await github_service.get_valid_access_token(1)

    assert token == "new_access"
    assert profile == external_profile


@pytest.mark.asyncio
async def test_get_valid_access_token_missing_profile(
    github_service: GithubService, mock_external_profile_repo: AsyncMock
) -> None:
    """Test error when external profile not found."""
    mock_external_profile_repo.get_external_profile_by_user_id.return_value = None
    with pytest.raises(GitHubIntegrationError):
        await github_service.get_valid_access_token(1)


@pytest.mark.asyncio
async def test_fetch_details_for_commits_with_empty_list(github_service: GithubService) -> None:
    """Test fetch_details_for_commits handles empty input."""
    result = await github_service.fetch_details_for_commits(AsyncMock(), [])
    assert result == []


@pytest.mark.asyncio
async def test_fetch_with_semaphore_missing_url(github_service: GithubService) -> None:
    """Test fetch_with_semaphore logs warning and returns None for commits without URLs."""
    commit = RepoCommit(
        sha="abc",
        url="https://api.github.com/repos/test/commits/abc",
        html_url="https://github.com/test/commit/abc",
        commit={
            "message": "Fix bug",
            "author": {"name": "octocat", "email": "octocat@example.com", "date": "2025-11-13T00:00:00Z"},
        },
    )
    client = AsyncMock()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "sha": "abc",
        "url": "https://api.github.com/repos/test/commits/abc",
        "html_url": "https://github.com/test/commit/abc",
        "commit": {
            "message": "Fix bug",
            "author": {
                "name": "octocat",
                "email": "octocat@example.com",
                "date": "2025-11-13T00:00:00Z",
            },
        },
        "stats": {
            "total": 10,
            "additions": 7,
            "deletions": 3,
        },
        "files": [
            {
                "sha": "file123",
                "filename": "main.py",
                "status": "modified",
                "additions": 5,
                "deletions": 2,
                "changes": 7,
                "blob_url": "https://github.com/test/commit/abc/blob/main.py",
                "raw_url": "https://github.com/test/raw/abc/main.py",
                "contents_url": "https://api.github.com/repos/test/contents/main.py?ref=abc",
            }
        ],
    }

    mock_response.raise_for_status.return_value = None

    client.get.return_value = mock_response

    result = await github_service.fetch_with_semaphore(client, commit)
    assert result.sha == "abc"


@pytest.mark.asyncio
async def test_get_commits_by_repo_id_success(
    github_service: GithubService, mock_external_profile_repo: AsyncMock, mock_github_repo: AsyncMock
) -> None:
    """
    Test that get_commits_by_repo_id retrieves the correct profile
    and calls the repository with the profile ID.
    """
    # --- Setup ---
    user_id = 123
    repo_id = 456
    profile_id = 789

    # Mock External Profile
    mock_profile = MagicMock(spec=ExternalProfile)
    mock_profile.id = profile_id
    mock_external_profile_repo.get_external_profile_by_user_id.return_value = mock_profile

    # Mock Commits return
    mock_commits = [MagicMock(), MagicMock()]
    mock_github_repo.get_commits_by_repo_id.return_value = mock_commits

    # --- Execute ---
    result = await github_service.get_commits_by_repo_id(repo_id, user_id)

    # --- Assert ---
    # 1. Verify profile lookup
    mock_external_profile_repo.get_external_profile_by_user_id.assert_called_once_with(user_id, PlatformEnum.GITHUB)

    # 2. Verify repo lookup using the retrieved profile ID
    mock_github_repo.get_commits_by_repo_id.assert_called_once_with(repo_id, profile_id)

    # 3. Verify final output
    assert result == mock_commits
    assert len(result) == 2


@pytest.mark.asyncio
async def test_generate_timeline_for_repo_success(
    github_service: GithubService,
    mock_github_repo: AsyncMock,
    mock_timeline_service: AsyncMock,
    mock_external_profile_repo: AsyncMock,
) -> None:
    # --- Setup ---
    user_id = 1
    token_data = MagicMock(sub=user_id)

    # Use a real Repository schema or ensure the Mock attributes are strings
    repo_mock = MagicMock()
    repo_mock.id = 101
    repo_mock.name = "TrackWise"  # Ensure this is a raw string
    repo_mock.full_name = "user/TrackWise"
    repo_mock.description = "Cool project"

    mock_github_repo.get_repo_by_id.return_value = repo_mock

    # Mock external profile with a real ID
    mock_profile = MagicMock()
    mock_profile.id = 50
    mock_external_profile_repo.get_external_profile_by_user_id.return_value = mock_profile

    # Mock commits as a list of real/mocked objects that won't fail validation
    mock_github_repo.get_commits_by_repo_id.return_value = [MagicMock(), MagicMock()]

    # Mock timeline creation return value
    created_timeline = MagicMock()
    created_timeline.id = 99
    mock_timeline_service.create_timeline.return_value = created_timeline

    # --- Execute ---
    await github_service.generate_timeline_for_repo(repo_mock, token_data)

    # --- Assert ---
    mock_timeline_service.create_timeline.assert_called_once()
    mock_timeline_service.generate_nodes_for_commits.assert_called_once_with(
        commits=mock_github_repo.get_commits_by_repo_id.return_value, timeline_id=99, repo_id=101, user_id=user_id
    )


@pytest.mark.asyncio
async def test_generate_all_github_timelines_multiple_repos(
    github_service: GithubService, mock_external_profile_repo: AsyncMock, mock_github_repo: AsyncMock
) -> None:
    # --- Setup ---
    token_data = MagicMock(sub=1)
    mock_profile = MagicMock(id=50)
    mock_external_profile_repo.get_external_profile_by_user_id.return_value = mock_profile

    # Mock two repositories in the DB
    repo1 = MagicMock(id=101)
    repo2 = MagicMock(id=102)
    mock_github_repo.get_db_repositories.return_value = [repo1, repo2]

    # Patch the single-repo method so we don't run the full logic twice
    with patch.object(github_service, "generate_timeline_for_repo", new_callable=AsyncMock) as mock_single_gen:
        # --- Execute ---
        await github_service.generate_all_github_timelines(token_data)

        # --- Assert ---
        assert mock_single_gen.call_count == 2
        mock_single_gen.assert_any_call(repo1, token_data)
        mock_single_gen.assert_any_call(repo2, token_data)


@pytest.mark.asyncio
async def test_generate_all_github_timelines_no_profile(
    github_service: GithubService, mock_external_profile_repo: AsyncMock
) -> None:
    # --- Setup ---
    token_data = MagicMock(sub=1)
    mock_external_profile_repo.get_external_profile_by_user_id.return_value = None

    # --- Execute & Assert ---
    with pytest.raises(GitHubIntegrationError) as exc:
        await github_service.generate_all_github_timelines(token_data)

    assert exc.value.details["error"] == "GitHub external profile not found"
