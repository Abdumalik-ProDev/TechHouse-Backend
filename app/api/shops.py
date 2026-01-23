import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.shop import (
    ShopCreate,
    ShopUpdate,
    ShopResponse,
    ShopDetailResponse,
)
from app.services.shop import ShopService
from app.services.product import ProductService

router = APIRouter(prefix="/shops", tags=["Shops"])


@router.post("", response_model=ShopResponse, status_code=status.HTTP_201_CREATED)
async def create_shop(
    request: ShopCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ShopResponse:
    service = ShopService(db)

    try:
        shop = await service.create_shop(
            name=request.name,
            owner_id=current_user.id,
            description=request.description,
        )
        return ShopResponse.model_validate(shop)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{shop_id}", response_model=ShopDetailResponse)
async def get_shop(
    shop_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ShopDetailResponse:
    service = ShopService(db)
    shop = await service.get_shop(shop_id)

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found",
        )

    product_service = ProductService(db)
    _, product_count = await product_service.get_shop_products(shop_id, skip=0, limit=1)

    response = ShopDetailResponse.model_validate(shop)
    response.product_count = product_count
    return response


@router.get("", response_model=dict)
async def list_shops(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> dict:
    service = ShopService(db)
    shops, total = await service.get_all_shops(skip, limit)

    return {
        "items": [ShopResponse.model_validate(s) for s in shops],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/user/my-shops", response_model=dict)
async def list_my_shops(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> dict:
    service = ShopService(db)
    shops, total = await service.get_user_shops(current_user.id, skip, limit)

    return {
        "items": [ShopResponse.model_validate(s) for s in shops],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.patch("/{shop_id}", response_model=ShopResponse)
async def update_shop(
    shop_id: uuid.UUID,
    request: ShopUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ShopResponse:
    service = ShopService(db)
    shop = await service.get_shop(shop_id)

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found",
        )

    if shop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this shop",
        )

    updated = await service.update_shop(
        shop_id,
        **request.model_dump(exclude_unset=True),
    )

    return ShopResponse.model_validate(updated)


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shop(
    shop_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = ShopService(db)
    shop = await service.get_shop(shop_id)

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found",
        )

    if shop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this shop",
        )

    await service.delete_shop(shop_id)
