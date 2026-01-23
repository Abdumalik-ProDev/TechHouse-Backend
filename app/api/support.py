import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.support import (
    SupportTicketCreate,
    SupportTicketUpdate,
    SupportTicketResponse,
    SupportTicketListResponse,
)
from app.services.support import SupportService

router = APIRouter(prefix="/support", tags=["Support"])


@router.post(
    "/tickets",
    response_model=SupportTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_support_ticket(
    request: SupportTicketCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SupportTicketResponse:
    service = SupportService(db)

    try:
        ticket = await service.create_ticket(
            user_id=current_user.id,
            subject=request.subject,
            description=request.description,
            priority=request.priority,
        )
        return SupportTicketResponse.model_validate(ticket)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SupportTicketResponse:
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found",
        )

    if ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ticket",
        )

    return SupportTicketResponse.model_validate(ticket)


@router.get("/tickets", response_model=SupportTicketListResponse)
async def list_my_tickets(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> SupportTicketListResponse:
    service = SupportService(db)
    tickets, total = await service.get_user_tickets(current_user.id, skip, limit)

    return SupportTicketListResponse(
        items=[SupportTicketResponse.model_validate(t) for t in tickets],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def update_support_ticket(
    ticket_id: uuid.UUID,
    request: SupportTicketUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SupportTicketResponse:
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found",
        )

    if ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ticket",
        )

    updated = await service.update_ticket(
        ticket_id,
        **request.model_dump(exclude_unset=True),
    )

    return SupportTicketResponse.model_validate(updated)


@router.post("/tickets/{ticket_id}/close", response_model=SupportTicketResponse)
async def close_support_ticket(
    ticket_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SupportTicketResponse:
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found",
        )

    if ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this ticket",
        )

    closed = await service.close_ticket(ticket_id)
    return SupportTicketResponse.model_validate(closed)
