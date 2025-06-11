from enum import Enum

from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum

from src.db.database import Base
from src.models.base import TimestampMixin


class PlatformEnum(str, Enum):
    GITHUB = "github"
    LINKEDIN = "linkedin"


class ExternalProfile(Base, TimestampMixin):
    __tablename__ = "external_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(SAEnum(PlatformEnum), nullable=False)
    platform_id = Column(String, nullable=False)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    profile_data = Column(JSON, nullable=True)
