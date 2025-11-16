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
    callback_data = response_callback.json()
    assert callback_data["access_token"] == "gho_12345_test_token"

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

