from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.repositories.usage_repository import UsageRepository
from app.schemas.usage import UsageSummary

router = APIRouter()


@router.get("/me", response_model=UsageSummary)
async def my_usage(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UsageSummary:
    return await UsageRepository(session).summarize_user(current_user.id)
