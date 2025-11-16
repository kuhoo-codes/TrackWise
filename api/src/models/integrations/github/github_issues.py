from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String

from src.db.database import Base
from src.models.base import TimestampMixin


class GithubIssue(Base, TimestampMixin):
    __tablename__ = "github_issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_profile_id = Column(Integer, ForeignKey("external_profiles.id", ondelete="CASCADE"), nullable=False)
    repository_id = Column(Integer, ForeignKey("github_repositories.id", ondelete="CASCADE"), nullable=False)
    github_issue_id = Column(BigInteger, nullable=False, unique=True, index=True)
    number = Column(Integer, nullable=False)
    state = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=True)
    html_url = Column(String, nullable=False)
    issue_created_at = Column(DateTime(timezone=True), nullable=False)
    issue_closed_at = Column(DateTime(timezone=True), nullable=True)
