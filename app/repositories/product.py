import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.sku == sku))
        return result.scalar_one_or_none()

    async def get_by_shop(
        self, shop_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Product], int]:
        total_result = await self.db.execute(
            select(func.count(Product.id)).where(Product.shop_id == shop_id)
        )
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(Product).where(Product.shop_id == shop_id).offset(skip).limit(limit)
        )
        products = result.scalars().all()
        return list(products), total

    async def get_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Product], int]:
        total_result = await self.db.execute(
            select(func.count(Product.id)).where(Product.category == category)
        )
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(Product)
            .where(Product.category == category)
            .offset(skip)
            .limit(limit)
        )
        products = result.scalars().all()
        return list(products), total

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Product], int]:
        total_result = await self.db.execute(select(func.count(Product.id)))
        total = total_result.scalar() or 0

        result = await self.db.execute(select(Product).offset(skip).limit(limit))
        products = result.scalars().all()
        return list(products), total

    async def update(self, product_id: uuid.UUID, **kwargs) -> Optional[Product]:
        product = await self.get_by_id(product_id)
        if not product:
            return None

        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product_id: uuid.UUID) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False

        await self.db.delete(product)
        await self.db.commit()
        return True
