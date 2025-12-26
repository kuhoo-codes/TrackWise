from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from src.schemas.base import TimestampSchema


class NodeType(str, Enum):
    WORK = "work"
    EDUCATION = "education"
    PROJECT = "project"
    MILESTONE = "milestone"
    CERTIFICATION = "certification"
    BLOG = "blog"


class DateGranularity(str, Enum):
    EXACT = "exact"
    MONTH = "month"
    YEAR = "year"
    SEASON = "season"


class TimelineNodeBase(BaseModel):
    parent_id: int | None = None
    title: str
    short_summary: str | None = None
    description: str | None = None
    private_notes: str | None = None
    type: NodeType
    start_date: datetime
    end_date: datetime | None = None
    is_current: bool = False
    date_granularity: DateGranularity = DateGranularity.EXACT
    github_repo_id: int | None = None
    github_pr_id: int | None = None


class TimelineNodeCreate(TimelineNodeBase):
    timeline_id: int


class TimelineNode(TimelineNodeCreate, TimestampSchema):
    id: int

    class Config:
        from_attributes = True


class TimelineNodeWithChildren(TimelineNode):
    children: list["TimelineNodeWithChildren"] = []

    class Config:
        from_attributes = True


class TimelineBase(BaseModel):
    title: str
    description: str | None = None
    slug: str | None = None
    is_public: bool = False
    default_zoom_level: int = 1


class TimelineCreate(TimelineBase):
    pass


class Timeline(TimelineBase, TimestampSchema):
    id: int
    user_id: int
    nodes: list[TimelineNodeWithChildren] = []

    class Config:
        from_attributes = True


class TimelineSummary(TimelineBase, TimestampSchema):
    id: int
    user_id: int

    class Config:
        from_attributes = True
