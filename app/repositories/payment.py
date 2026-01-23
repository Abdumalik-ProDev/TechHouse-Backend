import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_by_id(self, payment_id: uuid.UUID) -> Optional[Payment]:
        result = await self.db.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_reference(self, reference: str) -> Optional[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.reference == reference)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        total_result = await self.db.execute(
            select(func.count(Payment.id)).where(Payment.user_id == user_id)
        )
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(Payment).where(Payment.user_id == user_id).offset(skip).limit(limit)
        )
        payments = result.scalars().all()
        return list(payments), total

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        total_result = await self.db.execute(select(func.count(Payment.id)))
        total = total_result.scalar() or 0

        result = await self.db.execute(select(Payment).offset(skip).limit(limit))
        payments = result.scalars().all()
        return list(payments), total

    async def update(self, payment_id: uuid.UUID, **kwargs) -> Optional[Payment]:
        payment = await self.get_by_id(payment_id)
        if not payment:
            return None

        for key, value in kwargs.items():
            if hasattr(payment, key) and value is not None:
                setattr(payment, key, value)

        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def delete(self, payment_id: uuid.UUID) -> bool:
        payment = await self.get_by_id(payment_id)
        if not payment:
            return False

        await self.db.delete(payment)
        await self.db.commit()
        return True
