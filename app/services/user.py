import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[User], int]:
        return await self.user_repo.get_all(skip, limit)

    async def update_user(self, user_id: uuid.UUID, **kwargs) -> Optional[User]:
        return await self.user_repo.update(user_id, **kwargs)

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        return await self.user_repo.delete(user_id)

    async def upgrade_membership(
        self, user_id: uuid.UUID, membership_type: str
    ) -> Optional[User]:
        return await self.user_repo.update(user_id, membership_type=membership_type)
