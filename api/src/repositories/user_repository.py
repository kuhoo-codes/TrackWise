from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer

from src.models.users import User
from src.schemas.users import UserUpdate


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by their email address."""
        statement = select(User).filter(User.email == email).options(defer(User.avatar_blob))
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        """Create a new user in the database."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: int, profile_data: UserUpdate) -> User:
        """Update user metadata fields like name and headline."""
        statement = (
            update(User)
            .where(User.id == user_id)
            .values(**profile_data.model_dump(exclude_unset=True))
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(statement)
        await self.db.commit()

        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one()

    async def get_avatar_metadata(self, user_id: int) -> tuple[datetime, str] | None:
        """
        Fetches ONLY the timestamp and media type.
        Returns (updated_at, media_type) or None.
        """
        statement = select(User.updated_at, User.media_type).where(User.id == user_id)
        result = await self.db.execute(statement)
        row = result.fetchone()
        return (row.updated_at, row.media_type) if row else None

    async def get_avatar_blob(self, user_id: int) -> bytes | None:
        """
        Fetches the actual binary data.
        Returns bytes or None.
        """
        statement = select(User.avatar_blob).where(User.id == user_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def upload_avatar(self, user_id: int, blob: bytes, mime_type: str) -> None:
        """Update avatar fields using a direct update statement to avoid loading the object."""
        statement = update(User).where(User.id == user_id).values(avatar_blob=blob, media_type=mime_type)
        await self.db.execute(statement)
        await self.db.commit()

    async def remove_avatar(self, user_id: int) -> None:
        statement = (
            update(User)
            .where(User.id == user_id)
            .values(
                avatar_blob=None,
                media_type=None,
            )
        )
        await self.db.execute(statement)
        await self.db.commit()
