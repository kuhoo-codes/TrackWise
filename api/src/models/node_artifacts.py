from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from src.db.database import Base
from src.models.base import TimestampMixin


class NodeArtifact(Base, TimestampMixin):
    """Screenshots, PDF Certificates, Architecture Diagrams"""

    __tablename__ = "node_artifacts"
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("timeline_nodes.id", ondelete="CASCADE"), nullable=False)
    media_data = Column(LargeBinary, nullable=False)
    media_type = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    node = relationship("TimelineNode", back_populates="media")
