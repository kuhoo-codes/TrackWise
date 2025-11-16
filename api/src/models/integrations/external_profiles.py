from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum

from src.db.database import Base
from src.models.base import TimestampMixin


class PlatformEnum(str, Enum):
    GITHUB = "github"
    LINKEDIN = "linkedin"


class SyncStatusEnum(str, Enum):
    IDLE = "idle"  # Not running, or finished
    SYNCING = "syncing"  # A sync is currently in progress
    FAILED = "failed"  # The last sync failed
    COMPLETED = "completed"  # The last sync finished successfully


class SyncStepEnum(str, Enum):
    NONE = "none"  # Starting from scratch
    REPOS = "repos"  # Step 1 (repos) is done
    ISSUES = "issues"  # Step 2 (issues) is done
    COMMITS = "commits"  # Step 3 (commits) is done


class ExternalProfile(Base, TimestampMixin):
    __tablename__ = "external_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(SAEnum(PlatformEnum), nullable=False)
    external_username = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    access_token_expires_at = Column(DateTime(timezone=True))
    refresh_token_expires_at = Column(DateTime(timezone=True))
    last_synced_at = Column(DateTime, nullable=True, default=datetime.now())
    sync_status = Column(SAEnum(SyncStatusEnum), default=SyncStatusEnum.IDLE, nullable=False, index=True)
    sync_step = Column(SAEnum(SyncStepEnum), default=SyncStepEnum.NONE, nullable=False)
    last_sync_error = Column(String, nullable=True)
    last_sync_attempt_at = Column(DateTime(timezone=True), nullable=True)
