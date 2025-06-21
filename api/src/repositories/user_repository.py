from sqlalchemy.orm import Session

from src.models.users import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
