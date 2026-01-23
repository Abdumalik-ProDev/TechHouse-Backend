import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shop import Shop


class ShopRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, shop: Shop) -> Shop:
        self.db.add(shop)
        await self.db.commit()
        await self.db.refresh(shop)
        return shop

    async def get_by_id(self, shop_id: uuid.UUID) -> Optional[Shop]:
        result = await self.db.execute(select(Shop).where(Shop.id == shop_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Shop]:
        result = await self.db.execute(select(Shop).where(Shop.name == name))
        return result.scalar_one_or_none()

    async def get_by_owner(
        self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Shop], int]:
        total_result = await self.db.execute(
            select(func.count(Shop.id)).where(Shop.owner_id == owner_id)
        )
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(Shop).where(Shop.owner_id == owner_id).offset(skip).limit(limit)
        )
        shops = result.scalars().all()
        return list(shops), total

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Shop], int]:
        total_result = await self.db.execute(select(func.count(Shop.id)))
        total = total_result.scalar() or 0

        result = await self.db.execute(select(Shop).offset(skip).limit(limit))
        shops = result.scalars().all()
        return list(shops), total

    async def update(self, shop_id: uuid.UUID, **kwargs) -> Optional[Shop]:
        shop = await self.get_by_id(shop_id)
        if not shop:
            return None

        for key, value in kwargs.items():
            if hasattr(shop, key) and value is not None:
                setattr(shop, key, value)

        await self.db.commit()
        await self.db.refresh(shop)
        return shop

    async def delete(self, shop_id: uuid.UUID) -> bool:
        shop = await self.get_by_id(shop_id)
        if not shop:
            return False

        await self.db.delete(shop)
        await self.db.commit()
        return True
