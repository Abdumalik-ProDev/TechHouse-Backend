import uuid
import secrets
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.repositories.payment import PaymentRepository


class PaymentService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.payment_repo = PaymentRepository(db)

    async def create_payment(
        self,
        user_id: uuid.UUID,
        order_id: str,
        amount: float,
        method: str,
        notes: str | None = None,
    ) -> Payment:
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        if await self.payment_repo.get_by_order_id(order_id):
            raise ValueError(f"Payment for order '{order_id}' already exists")

        reference = self._generate_reference()

        payment = Payment(
            user_id=user_id,
            order_id=order_id,
            amount=amount,
            method=method,
            status="pending",
            reference=reference,
            notes=notes,
        )
        return await self.payment_repo.create(payment)

    async def get_payment(self, payment_id: uuid.UUID) -> Optional[Payment]:
        return await self.payment_repo.get_by_id(payment_id)

    async def get_payment_by_order(self, order_id: str) -> Optional[Payment]:
        return await self.payment_repo.get_by_order_id(order_id)

    async def get_user_payments(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        return await self.payment_repo.get_by_user(user_id, skip, limit)

    async def get_all_payments(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        return await self.payment_repo.get_all(skip, limit)

    async def process_payment(self, payment_id: uuid.UUID) -> Optional[Payment]:
        payment = await self.get_payment(payment_id)
        if not payment:
            return None

        if payment.status != "pending":
            raise ValueError(f"Cannot process payment with status '{payment.status}'")

        return await self.payment_repo.update(
            payment_id,
            status="completed",
            notes=f"{payment.notes or ''} Processed successfully".strip(),
        )

    async def fail_payment(
        self, payment_id: uuid.UUID, reason: str = ""
    ) -> Optional[Payment]:
        payment = await self.get_payment(payment_id)
        if not payment:
            return None

        notes = f"Failed: {reason}" if reason else "Payment failed"
        return await self.payment_repo.update(payment_id, status="failed", notes=notes)

    async def refund_payment(
        self, payment_id: uuid.UUID, reason: str = ""
    ) -> Optional[Payment]:
        payment = await self.get_payment(payment_id)
        if not payment:
            return None

        if payment.status != "completed":
            raise ValueError(
                f"Can only refund completed payments, this is '{payment.status}'"
            )

        notes = f"Refunded: {reason}" if reason else "Refunded"
        return await self.payment_repo.update(
            payment_id, status="refunded", notes=notes
        )

    async def update_payment_status(
        self, payment_id: uuid.UUID, status: str, notes: str | None = None
    ) -> Optional[Payment]:
        return await self.payment_repo.update(payment_id, status=status, notes=notes)

    @staticmethod
    def _generate_reference() -> str:
        return f"TXN-{secrets.token_hex(8).upper()}"
