from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt

from src.core.config import settings
from src.schemas.integrations.github import GitHubToken, StateRecord, TokenResponse


class GitHubRepository:
    def __init__(self) -> None:
        self.state_store: dict[str, StateRecord] = {}
        self.token_store: dict[str, GitHubToken] = {}

    async def save_state(self, state: str, user_id: str) -> None:
        """Save state to database/redis"""
        record = StateRecord(user_id=user_id, created_at=datetime.now())
        self.state_store[f"github:state:{state}"] = record

    async def validate_state(self, state: str) -> StateRecord:
        """Validate and return user_id associated with state"""
        record = self.state_store.get(f"github:state:{state}")
        if not record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter")

        if record.used:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State already used")
        record.used = True
        self.state_store[f"github:state:{state}"] = record

        return record

    async def save_token(self, user_id: str, token_data: dict) -> GitHubToken:
        """Store GitHub token data"""
        expires_in = datetime.now() + timedelta(seconds=token_data.get("expires_in", 6600))
        refresh_token_expires_in = datetime.now() + timedelta(seconds=token_data.get("refresh_token_expires_in", 6600))
        token = GitHubToken(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "bearer"),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope", ""),
            created_at=datetime.now(),
            expires_in=expires_in,
            refresh_token_expires_in=refresh_token_expires_in,
        )
        self.state_store[f"github:token:{user_id}"] = token

        return token

    async def create_access_token(self, user_id: str) -> TokenResponse:
        """Create JWT for your application"""
        to_encode = {"sub": user_id}
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return TokenResponse(access_token=access_token, token_type=settings.TOKEN_TYPE)
