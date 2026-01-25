from datetime import datetime

from pydantic import BaseModel

from src.models.integrations.github.github_commits import SignificanceLevel
from src.schemas.integrations.github import CommitInDB


class Cluster(BaseModel):
    id: str
    topic: str
    start_date: datetime
    end_date: datetime
    items: list[CommitInDB]
    primary_file_types: list[str]
    suggested_type: SignificanceLevel
    impact_score: float
    is_shallow: bool
