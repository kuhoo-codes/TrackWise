from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).filter(User.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
