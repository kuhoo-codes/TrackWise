from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import backref, relationship

from src.db.database import Base
from src.models.base import TimestampMixin


class NodeType(str, Enum):
    WORK = "work"
    EDUCATION = "education"
    PROJECT = "project"
    MILESTONE = "milestone"  # e.g., "Learned Python"
    CERTIFICATION = "certification"
    BLOG = "blog"


class DateGranularity(str, Enum):
    EXACT = "exact"  # Nov 18, 2025
    MONTH = "month"  # November 2025
    YEAR = "year"  # 2025
    SEASON = "season"


class TimelineNode(Base, TimestampMixin):
    __tablename__ = "timeline_nodes"

    id = Column(Integer, primary_key=True, index=True)
    timeline_id = Column(Integer, ForeignKey("timelines.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    short_summary = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    private_notes = Column(Text, nullable=True)
    type = Column(SAEnum(NodeType), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_current = Column(Boolean, default=False)
    date_granularity = Column(SAEnum(DateGranularity), default=DateGranularity.EXACT)
    github_repo_id = Column(Integer, ForeignKey("github_repositories.id"), nullable=True)
    github_pr_id = Column(Integer, nullable=True)
    parent_id = Column(Integer, ForeignKey("timeline_nodes.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    timeline = relationship("Timeline", back_populates="nodes")
    media = relationship("NodeArtifact", back_populates="node", cascade="all, delete-orphan")
    children = relationship("TimelineNode", backref=backref("parent", remote_side=[id]), cascade="all, delete-orphan")
