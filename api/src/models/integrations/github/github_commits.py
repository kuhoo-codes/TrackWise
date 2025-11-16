from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from src.db.database import Base


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
