import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ShopBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)


class ShopCreate(ShopBase):
    pass


class ShopUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=2000)
    is_active: bool | None = None


class ShopResponse(ShopBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ShopDetailResponse(ShopResponse):
    product_count: int | None = None