from sqlalchemy import Column, ForeignKey, Integer, String

from src.db.database import Base
from src.models.base import TimestampMixin


class TimelineConnection(Base, TimestampMixin):
    """
    Draws lines between nodes.
    e.g., "Learned React" (Source) -> "Built Portfolio" (Target)
    """

    __tablename__ = "timeline_connections"
    id = Column(Integer, primary_key=True, index=True)
    timeline_id = Column(Integer, ForeignKey("timelines.id", ondelete="CASCADE"), nullable=False)
    from_node_id = Column(Integer, ForeignKey("timeline_nodes.id", ondelete="CASCADE"), nullable=False)
    to_node_id = Column(Integer, ForeignKey("timeline_nodes.id", ondelete="CASCADE"), nullable=False)
    relationship_label = Column(String, nullable=True)
