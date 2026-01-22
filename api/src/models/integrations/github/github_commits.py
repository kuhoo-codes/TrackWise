from enum import Enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB

from src.db.database import Base


class SignificanceLevel(str, Enum):
    FEATURE = "FEATURE"  # High impact changes
    REFACTOR = "REFACTOR"  # Medium impact logic changes
    CHORE = "CHORE"  # Low impact/maintenance
    NOISE = "NOISE"  # Ignored/Zero impact


class GithubCommit(Base):
    __tablename__ = "github_commits"

    sha = Column(String, primary_key=True, index=True)
    external_profile_id = Column(Integer, ForeignKey("external_profiles.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, nullable=False)
    repository_id = Column(Integer, ForeignKey("github_repositories.id", ondelete="CASCADE"), nullable=False)
    message = Column(String, nullable=False)
    authored_at = Column(DateTime(timezone=True), nullable=False, index=True)
    html_url = Column(String, nullable=False)
    additions = Column(Integer, nullable=False)
    deletions = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    files = Column(JSONB, nullable=True)
    significance_score = Column(Float, nullable=True, default=0.0)
    significance_classification = Column(SAEnum(SignificanceLevel), nullable=True)
