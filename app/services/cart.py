import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.repositories.cart import CartRepository, CartItemRepository
from app.services.product import ProductService


class CartService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.cart_repo = CartRepository(db)
        self.item_repo = CartItemRepository(db)
        self.product_service = ProductService(db)

    async def get_user_cart(self, user_id: uuid.UUID) -> Optional[Cart]:
        return await self.cart_repo.get_by_user_id(user_id)

    async def add_item(
        self, cart_id: uuid.UUID, product_id: uuid.UUID, quantity: int
    ) -> Optional[CartItem]:
        product = await self.product_service.get_product(product_id)
        if not product:
            raise ValueError("Product not found")

        if not await self.product_service.check_availability(product_id, quantity):
            raise ValueError("Insufficient stock")

        existing_item = await self.item_repo.get_by_cart_and_product(
            cart_id, product_id
        )

        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if not await self.product_service.check_availability(
                product_id, new_quantity
            ):
                raise ValueError("Insufficient stock")
            return await self.item_repo.update(existing_item.id, quantity=new_quantity)

        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            price_at_addition=float(product.price),
        )
        return await self.item_repo.create(item)

    async def update_item_quantity(
        self, item_id: uuid.UUID, quantity: int
    ) -> Optional[CartItem]:
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            return None

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        if not await self.product_service.check_availability(item.product_id, quantity):
            raise ValueError("Insufficient stock")

        return await self.item_repo.update(item_id, quantity=quantity)

    async def remove_item(self, item_id: uuid.UUID) -> bool:
        return await self.item_repo.delete(item_id)

    async def clear_cart(self, cart_id: uuid.UUID) -> int:
        return await self.item_repo.clear_cart(cart_id)

    async def get_cart_total(self, cart_id: uuid.UUID) -> float:
        items = await self.item_repo.get_by_cart(cart_id)
        total = sum(float(item.price_at_addition) * item.quantity for item in items)
        return total

    async def get_cart_item_count(self, cart_id: uuid.UUID) -> int:
        items = await self.item_repo.get_by_cart(cart_id)
        return len(items)

    async def get_cart_quantity(self, cart_id: uuid.UUID) -> int:
        items = await self.item_repo.get_by_cart(cart_id)
        return sum(item.quantity for item in items)
