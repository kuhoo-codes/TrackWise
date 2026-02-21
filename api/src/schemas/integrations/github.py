from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from src.schemas.integrations.analysis.significance import SignificanceLevel


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


class UserBase(BaseModel):
    login: str
    id: int
    repos_url: str
    events_url: str
    type: str


class User(UserBase):
    name: str | None
    email: str | None


class CommitAuthor(BaseModel):
    name: str
    email: str
    date: datetime


class CommitData(BaseModel):
    message: str
    author: CommitAuthor | None = None


class RepoCommit(BaseModel):
    sha: str
    url: str
    html_url: str
    author: UserBase | None = None
    commit: CommitData


class CommitStat(BaseModel):
    additions: int
    deletions: int
    total: int


class CommitFile(BaseModel):
    sha: str
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    blob_url: str | None
    raw_url: str | None
    contents_url: str
    patch: str | None = None


class Commit(RepoCommit):
    stats: CommitStat
    files: list[CommitFile]
    significance_score: float | None = None
    significance_classification: SignificanceLevel | None = None


class CommitInDB(BaseModel):
    sha: str
    external_profile_id: int
    author_id: int
    repository_id: int
    message: str
    authored_at: datetime
    html_url: str
    additions: int
    deletions: int
    total: int
    files: list[dict] | None = None
    significance_score: float = 0.0
    significance_classification: SignificanceLevel | None = None

    class Config:
        from_attributes = True


class Repository(BaseModel):
    id: int
    fork: bool
    name: str
    full_name: str
    description: str | None
    html_url: str
    language: str | None
    stargazers_count: int
    forks_count: int
    fork: bool
    created_at: datetime
    updated_at: datetime
    commits: list[Commit] | None = None


class Issue(BaseModel):
    id: int
    url: str
    repository_url: str
    number: int
    state: str
    state_reason: str | None
    title: str
    body: str | None
    html_url: str
    locked: bool
    active_lock_reason: str | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    repository: Repository


class GithubAuthUrlResponse(BaseModel):
    authUrl: str
