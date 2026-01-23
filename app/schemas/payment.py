import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0, decimal_places=2)
    method: str = Field(
        ..., description="Payment method: credit_card, debit_card, bank_transfer, digital_wallet"
    )


class PaymentUpdate(BaseModel):
    status: str = Field(..., description="Payment status: pending, processing, completed, failed, refunded")
    notes: str | None = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    order_id: str
    amount: float
    method: str
    status: str
    reference: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    skip: int
    limit: int