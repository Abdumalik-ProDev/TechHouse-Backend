import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.enums import MembershipType

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.payment import Payment
    from app.models.support import SupportTicket


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    membership_type: Mapped[str] = mapped_column(
        String(20), default=MembershipType.BRONZE, nullable=False
    )

    cart: Mapped["Cart"] = relationship(back_populates="user", uselist=False)
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")
    support_tickets: Mapped[list["SupportTicket"]] = relationship(
        back_populates="user"
    )