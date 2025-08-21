from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from src.db.database import Base
from src.models.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    last_login = Column(DateTime, default=datetime.now(), nullable=True)
