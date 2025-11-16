from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from src.db.database import Base


class GithubRepository(Base):
    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_profile_id = Column(Integer, ForeignKey("external_profiles.id", ondelete="CASCADE"), nullable=False)
    github_repo_id = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    html_url = Column(String, nullable=False)
    language = Column(String, nullable=True, index=True)
    stargazers_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    is_fork = Column(Boolean, default=False)
    repo_created_at = Column(DateTime(timezone=True), nullable=False)
    repo_updated_at = Column(DateTime(timezone=True), nullable=False)
    last_commit_sync_at = Column(DateTime(timezone=True), nullable=True)
