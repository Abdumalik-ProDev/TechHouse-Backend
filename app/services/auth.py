from datetime import timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    decode_token,
)
from app.models.user import User
from app.models.cart import Cart
from app.repositories.user import UserRepository
from app.repositories.cart import CartRepository
from app.schemas.auth import Token
from app.core.config import get_settings


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.cart_repo = CartRepository(db)
        self.settings = get_settings()

    async def register_user(
        self, username: str, email: str, full_name: str, password: str
    ) -> User:
        if await self.user_repo.get_by_username(username):
            raise ValueError(f"Username '{username}' already exists")

        if await self.user_repo.get_by_email(email):
            raise ValueError(f"Email '{email}' already registered")

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        created_user = await self.user_repo.create(user)

        cart = Cart(user_id=created_user.id, status="active")
        await self.cart_repo.create(cart)

        return created_user

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_by_username(username)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    def create_access_token_for_user(
        self, user: User, expires_delta: Optional[timedelta] = None
    ) -> Token:
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
        }

        access_token = create_access_token(token_data, expires_delta)

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.settings.access_token_expire_minutes * 60,
        )

    async def get_user_from_token(self, token: str) -> Optional[User]:
        payload = decode_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        try:
            user = await self.user_repo.get_by_id(uuid.UUID(user_id))
            return user
        except ValueError:
            return None
