from __future__ import annotations

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AthenaError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)
        self.session = session

    async def register(self, email: str, password: str, full_name: str) -> User:
        existing = await self.users.get_by_email(email)
        if existing:
            raise AthenaError("A user with that email already exists", status.HTTP_409_CONFLICT)
        role = "admin" if email.lower().endswith("@admin.athena.local") else "developer"
        user = await self.users.create(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=role,
        )
        await self.session.commit()
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password) or not user.is_active:
            raise AthenaError("Invalid email or password", status.HTTP_401_UNAUTHORIZED)
        return create_access_token(user.id)
