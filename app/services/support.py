import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.support import SupportTicket
from app.repositories.user import UserRepository


class SupportService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self._ticket_counter = 1000

    async def create_ticket(
        self,
        user_id: uuid.UUID,
        subject: str,
        description: str,
        priority: str = "medium",
    ) -> SupportTicket:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        valid_priorities = ["low", "medium", "high", "critical"]
        if priority not in valid_priorities:
            raise ValueError(f"Invalid priority. Must be one of {valid_priorities}")

        ticket_number = self._generate_ticket_number()

        ticket = SupportTicket(
            ticket_number=ticket_number,
            user_id=user_id,
            subject=subject,
            description=description,
            priority=priority,
            status="open",
        )

        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def get_ticket(self, ticket_id: uuid.UUID) -> Optional[SupportTicket]:
        result = await self.db.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_user_tickets(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[SupportTicket], int]:
        total_result = await self.db.execute(
            select(func.count(SupportTicket.id)).where(SupportTicket.user_id == user_id)
        )
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(SupportTicket)
            .where(SupportTicket.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        tickets = result.scalars().all()

        return list(tickets), total

    async def get_all_tickets(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[SupportTicket], int]:
        total_result = await self.db.execute(select(func.count(SupportTicket.id)))
        total = total_result.scalar() or 0

        result = await self.db.execute(select(SupportTicket).offset(skip).limit(limit))
        tickets = result.scalars().all()

        return list(tickets), total

    async def update_ticket(
        self, ticket_id: uuid.UUID, **kwargs
    ) -> Optional[SupportTicket]:
        ticket = await self.get_ticket(ticket_id)
        if not ticket:
            return None

        for key, value in kwargs.items():
            if hasattr(ticket, key) and value is not None:
                setattr(ticket, key, value)

        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def close_ticket(
        self, ticket_id: uuid.UUID, resolution: str | None = None
    ) -> Optional[SupportTicket]:
        return await self.update_ticket(
            ticket_id, status="closed", resolution=resolution
        )

    async def reopen_ticket(self, ticket_id: uuid.UUID) -> Optional[SupportTicket]:
        return await self.update_ticket(ticket_id, status="open")

    @staticmethod
    def _generate_ticket_number() -> str:

        import time

        return f"TKT-{int(time.time())}"
