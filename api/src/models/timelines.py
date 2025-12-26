from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.db.database import Base
from src.models.base import TimestampMixin


class Timeline(Base, TimestampMixin):
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String, unique=True, index=True, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    default_zoom_level = Column(Integer, default=1)
    nodes = relationship("TimelineNode", back_populates="timeline", cascade="all, delete-orphan")
