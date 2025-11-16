from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, model_validator
from typing_extensions import Self


class GithubToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    scope: str | None = ""

    # GitHub raw fields
    expires_in: int
    refresh_token_expires_in: int

    # Computed fields
    created_at: datetime | None = None
    access_token_expires_at: datetime | None = None
    refresh_token_expires_at: datetime | None = None

    @model_validator(mode="after")
    def compute_expiry_dates(self) -> Self:
        now = datetime.now(timezone.utc)

        if not self.created_at:
            self.created_at = now

        self.access_token_expires_at = now + timedelta(seconds=self.expires_in)
        self.refresh_token_expires_at = now + timedelta(seconds=self.refresh_token_expires_in)

        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class StateRecord(BaseModel):
    user_id: int
    created_at: datetime
    used: bool = False
