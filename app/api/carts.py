import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartSummary
from app.services.cart import CartService

router = APIRouter(prefix="/carts", tags=["Shopping Cart"])


@router.get("/me", response_model=CartResponse)
async def get_my_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CartResponse:
    service = CartService(db)
    cart = await service.get_user_cart(current_user.id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    return CartResponse.model_validate(cart)


@router.get("/me/summary", response_model=CartSummary)
async def get_cart_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CartSummary:
    service = CartService(db)
    cart = await service.get_user_cart(current_user.id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    return CartSummary(
        id=cart.id,
        item_count=await service.get_cart_item_count(cart.id),
        total_items=await service.get_cart_quantity(cart.id),
        total_price=await service.get_cart_total(cart.id),
        status=cart.status,
    )


@router.post("/me/items", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    request: CartItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    service = CartService(db)
    cart = await service.get_user_cart(current_user.id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    try:
        item = await service.add_item(cart.id, request.product_id, request.quantity)
        return {"message": "Item added to cart", "item_id": str(item.id)}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/me/items/{item_id}")
async def update_cart_item(
    item_id: uuid.UUID,
    request: CartItemUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    service = CartService(db)

    try:
        item = await service.update_item_quantity(item_id, request.quantity)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found",
            )
        return {"message": "Item updated", "quantity": item.quantity}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/me/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = CartService(db)

    if not await service.remove_item(item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )


@router.delete("/me/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = CartService(db)
    cart = await service.get_user_cart(current_user.id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    await service.clear_cart(cart.id)
