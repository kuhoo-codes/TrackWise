from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from src.exceptions.auth import AuthenticationError, InvalidTokenError, TokenExpiredError, UserAlreadyExistsError
from src.models.users import User
from src.schemas.users import UserCreate
from src.services.auth_service import AuthService


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_repo: AsyncMock) -> AuthService:
    return AuthService(user_repo=mock_user_repo)


# --- Password and Token Tests ---


def test_hash_password(auth_service: AuthService) -> None:
    password = "plain_password"
    hashed_password = auth_service.hash_password(password)
    assert hashed_password != password
    assert auth_service.verify_password(password, hashed_password)


def test_verify_password_incorrect(auth_service: AuthService) -> None:
    password = "plain_password"
    hashed_password = auth_service.hash_password(password)
    assert not auth_service.verify_password("wrong_password", hashed_password)


def test_create_access_token(auth_service: AuthService) -> None:
    data = {"sub": "12424", "email": "test@example.com"}
    token = auth_service.create_access_token(data)
    decoded_payload = jwt.decode(token, auth_service.secret_key, algorithms=[auth_service.algorithm])
    assert decoded_payload["sub"] == data["sub"]
    assert decoded_payload["email"] == data["email"]
    assert "exp" in decoded_payload


# --- User Creation Tests ---


@pytest.mark.asyncio
async def test_create_user_success(auth_service: AuthService, mock_user_repo: AsyncMock) -> None:
    # --- Setup ---
    user_data = UserCreate(email="newuser@example.com", password="password@123", name="New User")
    mock_user_repo.get_user_by_email.return_value = None

    # --- Execute ---
    created_user_mock = User(id=1, email=user_data.email, name=user_data.name, hashed_password="hashed_password")
    mock_user_repo.create_user.return_value = created_user_mock

    result = await auth_service.create_user(user_data)

    # --- Assert ---
    assert result.email == user_data.email
    mock_user_repo.get_user_by_email.assert_called_once_with(user_data.email)
    mock_user_repo.create_user.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_already_exists(auth_service: AuthService, mock_user_repo: AsyncMock) -> None:
    # --- Setup ---
    user_data = UserCreate(email="existing@example.com", password="password@123", name="Existing User")
    mock_user_repo.get_user_by_email.return_value = User(id=1, email=user_data.email, name="Existing User")

    # --- Execute ---
    with pytest.raises(UserAlreadyExistsError):
        await auth_service.create_user(user_data)

    # --- Assert ---
    mock_user_repo.get_user_by_email.assert_called_once_with(user_data.email)
    mock_user_repo.create_user.assert_not_called()


# --- Authentication Tests ---


@pytest.mark.asyncio
async def test_authenticate_user_success(auth_service: AuthService, mock_user_repo: AsyncMock) -> None:
    # --- Setup ---
    email = "test@example.com"
    password = "password123"
    hashed_password = auth_service.hash_password(password)
    user_in_db = User(id=1, email=email, name="Test User", hashed_password=hashed_password)

    mock_user_repo.get_user_by_email.return_value = user_in_db

    # --- Execute ---
    authenticated_user = await auth_service.authenticate_user(email, password)

    # --- Assert ---
    assert authenticated_user.email == email
    mock_user_repo.get_user_by_email.assert_called_once_with(email)


@pytest.mark.asyncio
async def test_authenticate_user_not_found(auth_service: AuthService, mock_user_repo: AsyncMock) -> None:
    # --- Setup ---
    mock_user_repo.get_user_by_email.return_value = None

    # --- Execute and Assert ---
    with pytest.raises(AuthenticationError):
        await auth_service.authenticate_user("nonexistent@example.com", "password123")


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(auth_service: AuthService, mock_user_repo: AsyncMock) -> None:
    # --- Setup ---
    email = "test@example.com"
    password = "password123"
    hashed_password = auth_service.hash_password(password)
    user_in_db = User(id=1, email=email, name="Test User", hashed_password=hashed_password)

    mock_user_repo.get_user_by_email.return_value = user_in_db

    # --- Execute and Assert ---
    with pytest.raises(AuthenticationError):
        await auth_service.authenticate_user(email, "wrong_password")


# --- Token Verification and Blacklist Tests ---


@patch("src.services.auth_service.redis_client")
def test_verify_token_success(mock_redis: MagicMock, auth_service: AuthService) -> None:
    # --- Setup ---
    user_id = 63726732
    email = "test@example.com"
    mock_redis.exists.return_value = 0  # Not blacklisted
    token = auth_service.create_access_token(data={"sub": str(user_id), "email": email})

    # --- Execute ---
    data = auth_service.verify_token(token)

    # --- Assert ---
    assert data.email == email
    assert data.sub == user_id
    mock_redis.exists.assert_called_once_with(token)


@patch("src.services.auth_service.redis_client")
def test_verify_token_blacklisted(mock_redis: MagicMock, auth_service: AuthService) -> None:
    # --- Setup ---
    mock_redis.exists.return_value = 1  # Blacklisted
    token = auth_service.create_access_token(data={"sub": "test@example.com"})

    # --- Execute and Assert ---
    with pytest.raises(TokenExpiredError):
        auth_service.verify_token(token)


@patch("src.services.auth_service.redis_client")
def test_verify_token_expired(mock_redis: MagicMock, auth_service: AuthService) -> None:
    # --- Setup ---
    mock_redis.exists.return_value = 0

    expired_token = auth_service.create_access_token(data={"sub": "test@example.com"}, expires_delta=timedelta(days=-1))

    # --- Execute and Assert ---
    with pytest.raises(TokenExpiredError):
        auth_service.verify_token(expired_token)


@patch("src.services.auth_service.redis_client")
def test_verify_token_invalid_signature(mock_redis: MagicMock, auth_service: AuthService) -> None:
    # --- Setup ---
    mock_redis.exists.return_value = 0
    auth_service.secret_key = "a_different_secret_key"
    valid_token = jwt.encode({"sub": "test@example.com"}, "correct_key", algorithm=auth_service.algorithm)

    # --- Execute and Assert ---
    with pytest.raises(InvalidTokenError):
        auth_service.verify_token(valid_token)


@pytest.mark.asyncio
@patch("src.services.auth_service.redis_client")
async def test_add_to_blacklist(mock_redis: MagicMock, auth_service: AuthService) -> None:
    # --- Setup ---
    mock_redis.exists.return_value = 0
    token = "some_jwt_token"

    # --- Execute ---
    await auth_service.add_to_blacklist(token)

    # --- Assert ---
    mock_redis.set.assert_called_once_with(token, "blacklisted", ex=auth_service.access_token_expire_minutes * 60)
