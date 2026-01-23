import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem


class CartRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, cart: Cart) -> Cart:
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def get_by_id(self, cart_id: uuid.UUID) -> Optional[Cart]:
        result = await self.db.execute(select(Cart).where(Cart.id == cart_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Cart]:
        result = await self.db.execute(select(Cart).where(Cart.user_id == user_id))
        return result.scalar_one_or_none()

    async def update(self, cart_id: uuid.UUID, **kwargs) -> Optional[Cart]:
        cart = await self.get_by_id(cart_id)
        if not cart:
            return None

        for key, value in kwargs.items():
            if hasattr(cart, key) and value is not None:
                setattr(cart, key, value)

        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def delete(self, cart_id: uuid.UUID) -> bool:
        cart = await self.get_by_id(cart_id)
        if not cart:
            return False

        await self.db.delete(cart)
        await self.db.commit()
        return True


class CartItemRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, item: CartItem) -> CartItem:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_by_id(self, item_id: uuid.UUID) -> Optional[CartItem]:
        result = await self.db.execute(select(CartItem).where(CartItem.id == item_id))
        return result.scalar_one_or_none()

    async def get_by_cart_and_product(
        self, cart_id: uuid.UUID, product_id: uuid.UUID
    ) -> Optional[CartItem]:
        result = await self.db.execute(
            select(CartItem).where(
                (CartItem.cart_id == cart_id) & (CartItem.product_id == product_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_cart(self, cart_id: uuid.UUID) -> list[CartItem]:
        result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id)
        )
        return list(result.scalars().all())

    async def update(self, item_id: uuid.UUID, **kwargs) -> Optional[CartItem]:
        item = await self.get_by_id(item_id)
        if not item:
            return None

        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, item_id: uuid.UUID) -> bool:
        item = await self.get_by_id(item_id)
        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True

    async def clear_cart(self, cart_id: uuid.UUID) -> int:
        items = await self.get_by_cart(cart_id)
        count = len(items)
        for item in items:
            await self.db.delete(item)
        await self.db.commit()
        return count
