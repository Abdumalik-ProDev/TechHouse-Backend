import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.product import ProductRepository


class ProductService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.product_repo = ProductRepository(db)

    async def create_product(
        self,
        name: str,
        price: float,
        stock: int,
        category: str,
        sku: str,
        shop_id: uuid.UUID,
        description: str | None = None,
    ) -> Product:
        if await self.product_repo.get_by_sku(sku):
            raise ValueError(f"SKU '{sku}' already exists")

        product = Product(
            name=name,
            price=price,
            stock=stock,
            category=category,
            sku=sku,
            shop_id=shop_id,
            description=description,
        )
        return await self.product_repo.create(product)

    async def get_product(self, product_id: uuid.UUID) -> Optional[Product]:
        return await self.product_repo.get_by_id(product_id)

    async def get_all_products(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Product], int]:
        return await self.product_repo.get_all(skip, limit)

    async def get_shop_products(
        self, shop_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Product], int]:
        return await self.product_repo.get_by_shop(shop_id, skip, limit)

    async def get_category_products(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Product], int]:
        return await self.product_repo.get_by_category(category, skip, limit)

    async def update_product(
        self, product_id: uuid.UUID, **kwargs
    ) -> Optional[Product]:
        return await self.product_repo.update(product_id, **kwargs)

    async def delete_product(self, product_id: uuid.UUID) -> bool:
        return await self.product_repo.delete(product_id)

    async def update_stock(
        self, product_id: uuid.UUID, quantity: int
    ) -> Optional[Product]:
        product = await self.get_product(product_id)
        if not product:
            return None

        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative")

        return await self.product_repo.update(product_id, stock=quantity)

    async def check_availability(self, product_id: uuid.UUID, quantity: int) -> bool:
        product = await self.get_product(product_id)
        return bool(product and product.stock >= quantity)
