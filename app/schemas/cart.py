import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(default=1, ge=1, le=1000)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, le=1000)


class CartItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    price_at_addition: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    items: list[CartItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CartSummary(BaseModel):
    id: uuid.UUID
    item_count: int
    total_items: int
    total_price: float
    status: str