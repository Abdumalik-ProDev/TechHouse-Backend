import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shop import Shop
from app.repositories.shop import ShopRepository


class ShopService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.shop_repo = ShopRepository(db)

    async def create_shop(
        self, name: str, owner_id: uuid.UUID, description: str | None = None
    ) -> Shop:
        if await self.shop_repo.get_by_name(name):
            raise ValueError(f"Shop name '{name}' already exists")

        shop = Shop(
            name=name, owner_id=owner_id, description=description, is_active=True
        )
        return await self.shop_repo.create(shop)

    async def get_shop(self, shop_id: uuid.UUID) -> Optional[Shop]:
        return await self.shop_repo.get_by_id(shop_id)

    async def get_all_shops(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Shop], int]:
        return await self.shop_repo.get_all(skip, limit)

    async def get_user_shops(
        self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Shop], int]:
        return await self.shop_repo.get_by_owner(owner_id, skip, limit)

    async def update_shop(self, shop_id: uuid.UUID, **kwargs) -> Optional[Shop]:
        return await self.shop_repo.update(shop_id, **kwargs)

    async def delete_shop(self, shop_id: uuid.UUID) -> bool:
        return await self.shop_repo.delete(shop_id)

    async def toggle_shop_status(self, shop_id: uuid.UUID) -> Optional[Shop]:
        shop = await self.get_shop(shop_id)
        if not shop:
            return None

        return await self.shop_repo.update(shop_id, is_active=not shop.is_active)
