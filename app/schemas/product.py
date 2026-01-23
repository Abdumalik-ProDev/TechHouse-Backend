import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    price: float = Field(..., gt=0, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    category: str = Field(..., min_length=1, max_length=100)
    sku: str = Field(..., min_length=1, max_length=50)


class ProductCreate(ProductBase):
    shop_id: uuid.UUID


class ProductUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=2000)
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category: str | None = Field(None, max_length=100)


class ProductResponse(ProductBase):
    id: uuid.UUID
    shop_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int