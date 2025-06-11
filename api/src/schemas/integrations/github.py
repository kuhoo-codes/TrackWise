from datetime import datetime

from pydantic import BaseModel


class GitHubToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    scope: str
    created_at: datetime
    expires_in: datetime
    refresh_token_expires_in: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class StateRecord(BaseModel):
    user_id: str
    created_at: datetime
    used: bool = False


class TokenData(BaseModel):
    user_id: str
