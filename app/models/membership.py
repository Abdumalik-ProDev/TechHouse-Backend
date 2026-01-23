import uuid

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from app.utils.enums import MembershipType


class Membership(BaseModel):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    tier: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    discount_percentage: Mapped[float] = mapped_column(
        Numeric(precision=5, scale=2), default=0, nullable=False
    )
    annual_fee: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=2), default=0, nullable=False
    )