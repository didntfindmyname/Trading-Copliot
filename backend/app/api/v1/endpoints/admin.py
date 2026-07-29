from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.pagination import Page
from app.db.session import get_session
from app.models.user import User
from app.repositories.usage_repository import UsageRepository
from app.repositories.user_repository import UserRepository
from app.schemas.usage import AdminUsageSummary
from app.schemas.user import UserRead

router = APIRouter()


@router.get("/users", response_model=Page[UserRead])
async def users(
    limit: int = 25,
    offset: int = 0,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> Page[UserRead]:
    _ = admin
    items, total = await UserRepository(session).list(limit, offset)
    return Page[UserRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/usage", response_model=AdminUsageSummary)
async def usage(
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> AdminUsageSummary:
    _ = admin
    return await UsageRepository(session).summarize_admin()
