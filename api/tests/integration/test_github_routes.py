import json
from collections.abc import Generator
from unittest.mock import ANY, AsyncMock, MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from tests.test_helpers import AuthHelper


@pytest.fixture(autouse=True)
def mock_redis_client(monkeypatch: MonkeyPatch) -> Generator[MagicMock, None, None]:
    """Automatically mock Redis client for all tests."""
    mock = MagicMock()
    mock.exists.return_value = 0
    mock.get.return_value = None
    mock.set.return_value = None
    mock.delete.return_value = None
    mock.ping.return_value = True

    monkeypatch.setattr("src.core.redis_utils.redis_client", mock)
    monkeypatch.setattr("src.services.auth_service.redis_client", mock, raising=False)
    monkeypatch.setattr("src.services.integrations.github_service.redis_client", mock, raising=False)
    monkeypatch.setattr("src.repositories.integrations.github_repository.redis_client", mock, raising=False)
    yield mock


@patch("httpx.AsyncClient.get")
@patch("httpx.AsyncClient.post")
def test_github_auth_flow(
    mock_httpx_post: AsyncMock,
    mock_httpx_get: AsyncMock,
    client: TestClient,
    auth_helper: AuthHelper,
    mock_redis_client: MagicMock,
) -> None:
    """Tests the full GitHub auth flow, from getting a URL to the callback."""

    # --- Setup ---

    # Mock for POST /login/oauth/access_token
    mock_token_api_response = MagicMock()
    mock_token_api_response.status_code = 200
    mock_token_api_response.json.return_value = {
        "access_token": "gho_12345_test_token",
        "token_type": "bearer",
        "scope": "repo,user",
        "expires_in": 288000,
        "refresh_token": "ghr_67890_test_refresh_token",
        "refresh_token_expires_in": 16070400,
    }
    mock_httpx_post.return_value = mock_token_api_response

    # 3. ADDED: Mock for GET /user
    mock_user_api_response = MagicMock()
    mock_user_api_response.status_code = 200
    mock_user_api_response.json.return_value = {
        "id": 123456,  # This is the external GitHub user ID
        "login": "appa-on-github",  # This is the external username
        "name": "Appa Singh",
        "repos_url": "https://api.github.com/user/repos",
        "events_url": "https://api.github.com/users/appa-on-github/events{/privacy}",
        "type": "User",
        "email": "appa@email.com",
    }
    mock_user_api_response.raise_for_status = MagicMock()
    mock_httpx_get.return_value = mock_user_api_response

    appa_headers = auth_helper.get_auth_headers("appa")
    appa_id = auth_helper.get_predefined_user("appa")["user"]["id"]

    # --- Run Test ---
    response_url = client.get("/integrations/github/auth-url", headers=appa_headers)
    assert response_url.status_code == 200
    data = response_url.json()

    parsed_url = urlparse(data["authUrl"])
    query_params = parse_qs(parsed_url.query)
    state = query_params["state"][0]
    state_key = f"github:state:{state}"

    mock_redis_client.set.assert_called_with(state_key, ANY, ex=1800)
    saved_state_json = mock_redis_client.set.call_args[0][1]
    saved_state_data = json.loads(saved_state_json)
    assert saved_state_data["user_id"] == appa_id
    mock_redis_client.get.return_value = saved_state_json

    test_code = "abc123_test_code"
    response_callback = client.get(f"/integrations/github/callback?code={test_code}&state={state}")

    # --- Assert ---
    assert response_callback.status_code == 200

    mock_httpx_post.assert_awaited_once()
    assert mock_httpx_post.call_args.args[0] == "https://github.com/login/oauth/access_token"

    mock_httpx_get.assert_awaited_once()
    assert mock_httpx_get.call_args.args[0] == "https://api.github.com/user"
    auth_header = mock_httpx_get.call_args.kwargs["headers"]["Authorization"]
    assert auth_header == "Bearer gho_12345_test_token"
    mock_redis_client.get.assert_called_with(state_key)

    assert mock_redis_client.set.call_count == 3
    token_key = f"github:token:{appa_id}"
    token_set_call = mock_redis_client.set.call_args
    assert token_set_call[0][0] == token_key
    assert token_set_call[1]["ex"] == 288000
    assert json.loads(token_set_call[0][1])["access_token"] == "gho_12345_test_token"


@patch("httpx.AsyncClient.get")
@patch("httpx.AsyncClient.post")
def test_start_github_sync_success(
    mock_httpx_post: AsyncMock,
    mock_httpx_get: AsyncMock,
    client: TestClient,
    auth_helper: AuthHelper,
) -> None:
    """Test starting GitHub sync successfully."""

    # --- Setup Mock for POST (for token refresh) ---
    mock_token_api_response = MagicMock()
    mock_token_api_response.status_code = 200
    mock_token_api_response.json.return_value = {
        "access_token": "gho_12345_test_token",
        "token_type": "bearer",
        "scope": "repo,user",
        "expires_in": 288000,
        "refresh_token": "ghr_67890_test_refresh_token",
        "refresh_token_expires_in": 16070400,
    }
    mock_httpx_post.return_value = mock_token_api_response

    # --- Setup Mock for GET (for all sync calls) ---
    mock_sync_api_response = MagicMock()
    mock_sync_api_response.status_code = 200
    # Return an empty list to satisfy repos, issues, etc.
    mock_sync_api_response.json.return_value = []
    mock_sync_api_response.raise_for_status = MagicMock()
    mock_httpx_get.return_value = mock_sync_api_response

    # --- Run Test ---
    appa_headers = auth_helper.get_auth_headers("appa")
    response = client.get("/integrations/github/sync", headers=appa_headers)
    data = response.json()

    # --- Assert ---
    assert response.status_code == 200
    assert "GitHub synchronization has been started" in data["message"]
    mock_httpx_get.assert_called()


def test_start_github_sync_failure(
    client: TestClient,
    auth_helper: AuthHelper,
) -> None:
    """Test starting GitHub sync successfully."""

    # --- Run Test ---
    appa_headers = auth_helper.get_auth_headers("momo")
    response = client.get("/integrations/github/sync", headers=appa_headers)
    data = response.json()

    # --- Assert ---
    assert response.status_code == 502
    assert "error" in data
    assert data["error"]["code"] == "GITHUB_INTEGRATION_ERROR"
    assert data["error"]["message"] == "GitHub integration error"
    assert data["error"]["details"] == {"error": "GitHub external profile not found"}


def test_get_github_sync_status_connected(
    client: TestClient,
    auth_helper: AuthHelper,
) -> None:
    """Test retrieving sync status for a connected user."""
    # --- Setup ---
    appa_headers = auth_helper.get_auth_headers("appa")
    mock_at = "2025-11-13T00:00:00Z"

    mock_status_response = {
        "is_connected": True,
        "sync_status": "completed",
        "last_synced_at": mock_at,
        "last_sync_error": None,
    }

    with patch(
        "src.services.integrations.github_service.GithubService.get_sync_status", new_callable=AsyncMock
    ) as mock_get_status:
        mock_get_status.return_value = mock_status_response

        # --- Execute ---
        response = client.get("/integrations/github/sync-status", headers=appa_headers)
        data = response.json()

        # --- Assert ---
        assert response.status_code == 200
        assert data["is_connected"] is True
        assert data["sync_status"] == "completed"


def test_get_github_sync_status_not_connected(
    client: TestClient,
    auth_helper: AuthHelper,
) -> None:
    """Test retrieving sync status for a user who hasn't connected GitHub yet."""
    # --- Setup ---
    momo_headers = auth_helper.get_auth_headers("momo")

    mock_status_response = {
        "is_connected": False,
        "sync_status": "idle",
        "last_synced_at": None,
        "last_sync_error": None,
    }

    with patch(
        "src.services.integrations.github_service.GithubService.get_sync_status", new_callable=AsyncMock
    ) as mock_get_status:
        mock_get_status.return_value = mock_status_response

        # --- Execute ---
        response = client.get("/integrations/github/sync-status", headers=momo_headers)
        data = response.json()

        # --- Assert ---
        assert response.status_code == 200
        assert data["is_connected"] is False
        assert data["sync_status"] == "idle"
        assert data["last_synced_at"] is None


def test_get_github_sync_status_unauthorized(
    client: TestClient,
) -> None:
    """Test that the endpoint requires a valid auth token."""
    # --- Execute ---
    response = client.get("/integrations/github/sync-status")

    # --- Assert ---
    assert response.status_code == 403


def test_get_github_repositories_success(
    client: TestClient,
    auth_helper: AuthHelper,
) -> None:
    """Test retrieving GitHub repositories successfully."""

    appa_headers = auth_helper.get_auth_headers("appa")
    appa_id = auth_helper.get_predefined_user("appa")["user"]["id"]

    mock_repos = [
        {
            "id": 1,
            "name": "repo-one",
            "full_name": "appa/repo-one",
            "description": "First test repository",
            "html_url": "https://github.com/appa/repo-one",
            "language": "Python",
            "stargazers_count": 10,
            "forks_count": 2,
            "external_profile_id": 101,
            "github_repo_id": 987654,
            "is_fork": False,
            "repo_created_at": "2024-01-01T00:00:00Z",
            "repo_updated_at": "2024-02-01T00:00:00Z",
            "generation_status": "idle",
        },
        {
            "id": 2,
            "name": "repo-two",
            "full_name": "appa/repo-two",
            "description": "Second test repository",
            "html_url": "https://github.com/appa/repo-two",
            "language": "TypeScript",
            "stargazers_count": 5,
            "forks_count": 1,
            "external_profile_id": 101,
            "github_repo_id": 123456,
            "is_fork": True,
            "repo_created_at": "2023-06-10T00:00:00Z",
            "repo_updated_at": "2023-07-15T00:00:00Z",
            "generation_status": "completed",
        },
    ]

    with patch(
        "src.services.integrations.github_service.GithubService.get_all_repositories",
        new_callable=AsyncMock,
    ) as mock_get_repos:
        mock_get_repos.return_value = mock_repos

        response = client.get(
            "/integrations/github/repositories",
            headers=appa_headers,
        )

        data = response.json()

        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "repo-one"
        assert data[1]["is_fork"] is True

        mock_get_repos.assert_awaited_once_with(user_id=appa_id)


def test_get_github_repositories_empty(
    client: TestClient,
    auth_helper: AuthHelper,
) -> None:
    """Test retrieving repositories when none exist."""

    appa_headers = auth_helper.get_auth_headers("appa")
    appa_id = auth_helper.get_predefined_user("appa")["user"]["id"]

    with patch(
        "src.services.integrations.github_service.GithubService.get_all_repositories",
        new_callable=AsyncMock,
    ) as mock_get_repos:
        mock_get_repos.return_value = []

        response = client.get(
            "/integrations/github/repositories",
            headers=appa_headers,
        )

        data = response.json()

        assert response.status_code == 200
        assert data == []

        mock_get_repos.assert_awaited_once_with(user_id=appa_id)


def test_get_github_repositories_unauthorized(
    client: TestClient,
) -> None:
    """Test endpoint requires authentication."""

    response = client.get("/integrations/github/repositories")

    assert response.status_code == 403


def test_generate_github_timelines_success(
    client: TestClient,
    auth_helper: AuthHelper,
) -> None:
    """Test starting timeline generation successfully."""

    appa_headers = auth_helper.get_auth_headers("appa")

    with (
        patch(
            "src.services.integrations.github_service.GithubService.generate_github_timelines",
            new_callable=AsyncMock,
        ) as mock_generate,
        patch(
            "src.repositories.integrations.github_repository.GithubRepository.lock_repos_for_timeline_generation",
            new_callable=AsyncMock,
        ) as mock_lock,
    ):
        # Lock returns repo ids (means available for processing)
        mock_lock.return_value = [1, 2, 3]

        response = client.post(
            "/integrations/github/timelines",
            json=[1, 2, 3],  # IMPORTANT: raw list because endpoint expects list[int]
            headers=appa_headers,
        )

        data = response.json()

        assert response.status_code == 202
        assert data["status"] == "accepted"
        assert "started" in data["message"]

        mock_lock.assert_awaited_once_with(repo_ids=[1, 2, 3])
        mock_generate.assert_called_once()


def test_generate_github_timelines_all_locked(
    client: TestClient,
    auth_helper: AuthHelper,
) -> None:
    """Test when all selected repositories are already being processed."""

    appa_headers = auth_helper.get_auth_headers("appa")

    with patch(
        "src.repositories.integrations.github_repository.GithubRepository.lock_repos_for_timeline_generation",
        new_callable=AsyncMock,
    ) as mock_lock:
        # Nothing available for processing
        mock_lock.return_value = []

        response = client.post(
            "/integrations/github/timelines",
            json=[1, 2],
            headers=appa_headers,
        )

        data = response.json()

        assert response.status_code == 202
        assert data["status"] == "queued"
        assert "currently being processed" in data["message"]

        mock_lock.assert_awaited_once_with(repo_ids=[1, 2])


def test_generate_github_timelines_unauthorized(
    client: TestClient,
) -> None:
    """Test endpoint requires authentication."""

    response = client.post(
        "/integrations/github/timelines",
        json=[1, 2, 3],
    )

    assert response.status_code == 403
