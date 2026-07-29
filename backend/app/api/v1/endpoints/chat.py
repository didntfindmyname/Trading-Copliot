from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.pagination import Page
from app.db.session import get_session
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ConversationRead

router = APIRouter()


@router.get("/conversations", response_model=Page[ConversationRead])
async def conversations(
    limit: int = 25,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Page[ConversationRead]:
    items, total = await ConversationRepository(session).list_for_user(
        current_user.id, limit, offset
    )
    return Page[ConversationRead](items=items, total=total, limit=limit, offset=offset)
