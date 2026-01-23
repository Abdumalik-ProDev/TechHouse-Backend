import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SupportTicketCreate(BaseModel):
    subject: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10, max_length=5000)
    priority: str = Field(
        default="medium",
        description="Priority level: low, medium, high, critical",
    )


class SupportTicketUpdate(BaseModel):
    subject: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=5000)
    status: str | None = Field(
        None, description="Status: open, in_progress, resolved, closed"
    )
    priority: str | None = Field(None, description="Priority: low, medium, high, critical")
    resolution: str | None = Field(None, max_length=5000)


class SupportTicketResponse(BaseModel):
    id: uuid.UUID
    ticket_number: str
    user_id: uuid.UUID
    subject: str
    description: str
    priority: str
    status: str
    resolution: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupportTicketListResponse(BaseModel):
    items: list[SupportTicketResponse]
    total: int
    skip: int
    limit: int