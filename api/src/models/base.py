from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(),
        onupdate=datetime.now(),
        nullable=False,
    )
