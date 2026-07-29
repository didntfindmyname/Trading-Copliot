from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def get(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)

    async def list(self, limit: int, offset: int) -> tuple[list[User], int]:
        users = (
            (await self.session.execute(select(User).limit(limit).offset(offset))).scalars().all()
        )
        total = len((await self.session.execute(select(User.id))).scalars().all())
        return list(users), total

    async def create(
        self, email: str, full_name: str, hashed_password: str, role: str = "developer"
    ) -> User:
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hashed_password,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        return user
