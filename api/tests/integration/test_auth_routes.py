from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_signup_success(client: TestClient) -> None:
    """Test successful user signup."""
    # --- Execute ---
    response = client.post(
        "/auth/signup",
        json={"email": "testuser@example.com", "password": "Password@123", "name": "Test User"},
    )
    data = response.json()

    # --- Assert ---
    assert response.status_code == 201
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["name"] == "Test User"
    assert "created_at" in data["user"]
    assert "updated_at" in data["user"]
    assert "last_login" in data["user"]
    assert "id" in data["user"]


def test_signup_user_already_exists(client: TestClient) -> None:
    """Test signup with an email that already exists."""
    # --- Execute ---
    client.post(
        "/auth/signup",
        json={"email": "existing@example.com", "password": "Password@123", "name": "Existing User"},
    )
    response = client.post(
        "/auth/signup",
        json={"email": "existing@example.com", "password": "Password@123", "name": "Existing User"},
    )
    data = response.json()

    # --- Assert ---
    assert response.status_code == 409
    assert data["error"]["code"] == "USER_ALREADY_EXISTS"
    assert data["error"]["message"] == "User with this email already exists"
    assert "timestamp" in data["error"]
    assert data["error"]["details"]["email"] == "existing@example.com"


def test_login_success(client: TestClient) -> None:
    """Test successful user login."""
    # --- Execute ---
    signup_payload = {"email": "loginuser@example.com", "password": "Password@123", "name": "Login User"}
    client.post("/auth/signup", json=signup_payload)

    login_payload = {"email": "loginuser@example.com", "password": "Password@123"}
    response = client.post("/auth/login", json=login_payload)
    data = response.json()

    # --- Assert ---
    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["email"] == "loginuser@example.com"
    assert data["user"]["name"] == "Login User"
    assert "created_at" in data["user"]
    assert "updated_at" in data["user"]
    assert "last_login" in data["user"]
    assert "id" in data["user"]


def test_login_user_not_found(client: TestClient) -> None:
    """Test login with a non-existent email."""
    # --- Execute ---
    response = client.post("/auth/login", json={"email": "nouser@example.com", "password": "Password@123"})
    data = response.json()

    # --- Assert ---
    assert response.status_code == 401
    assert data["error"]["code"] == "AUTH_FAILED"
    assert data["error"]["message"] == "Invalid email or password"
    assert "timestamp" in data["error"]
    assert data["error"]["details"]["email"] == "nouser@example.com"


def test_login_wrong_password(client: TestClient) -> None:
    """Test login with an incorrect password."""
    # --- Execute ---
    signup_payload = {"email": "wrongpass@example.com", "password": "Password@123", "name": "Wrong Pass"}
    client.post("/auth/signup", json=signup_payload)

    login_payload = {"email": "wrongpass@example.com", "password": "wrongpassword"}
    response = client.post("/auth/login", json=login_payload)
    data = response.json()

    # --- Assert ---
    assert response.status_code == 401
    assert data["error"]["code"] == "AUTH_FAILED"
    assert data["error"]["message"] == "Invalid email or password"
    assert "timestamp" in data["error"]
    assert data["error"]["details"]["email"] == "wrongpass@example.com"


@patch("src.services.auth_service.redis_client")
def test_get_me_success(mock_redis: MagicMock, client: TestClient) -> None:
    """Test fetching current user data with a valid token."""
    # --- Execute ---
    signup_payload = {"email": "me@example.com", "password": "Password@123", "name": "Me User"}
    client.post("/auth/signup", json=signup_payload)
    login_response = client.post("/auth/login", json=signup_payload).json()

    token = login_response["access_token"]

    mock_redis.exists.return_value = 0

    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/auth/me", headers=headers)
    data = me_response.json()

    # --- Assert ---
    assert me_response.status_code == 200
    assert data["email"] == "me@example.com"
    assert data["name"] == "Me User"
    assert "created_at" in data
    assert "updated_at" in data
    assert "last_login" in data
    assert "id" in data


def test_get_me_unauthorized(client: TestClient) -> None:
    """Test fetching /me without an authorization header."""
    # --- Execute ---
    response = client.get("/auth/me")
    data = response.json()

    # --- Assert ---
    assert response.status_code == 403  # FastAPI's default for missing credentials
    assert data["error"]["code"] == "HTTP_ERROR"
    assert data["error"]["message"] == "Not authenticated"
    assert "timestamp" in data["error"]


@patch("src.services.auth_service.redis_client")
def test_logout_and_token_invalidation(mock_redis: MagicMock, client: TestClient) -> None:
    """Test that a logged-out token can no longer be used."""
    # --- Execute ---
    signup_payload = {"email": "logout@example.com", "password": "Password@123", "name": "Logout User"}
    client.post("/auth/signup", json=signup_payload)
    login_response = client.post("/auth/login", json={"email": "logout@example.com", "password": "Password@123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = client.delete("/auth/logout", headers=headers)

    mock_redis.exists.return_value = 1

    me_response = client.get("/auth/me", headers=headers)
    data = me_response.json()

    # --- Assert ---
    assert logout_response.status_code == 204  # No Content

    assert me_response.status_code == 401  # Unauthorized
    assert data["error"]["code"] == "TOKEN_EXPIRED"
    assert data["error"]["message"] == "Token has expired"
    assert "timestamp" in data["error"]
