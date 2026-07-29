from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_redis
from app.db.session import get_session
from app.models.user import User
from app.schemas.chat import AskRequest, AskResponse
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> AskResponse | StreamingResponse:
    service = RagService(session, redis=redis)
    if payload.stream:
        return StreamingResponse(
            service.stream(
                user=current_user,
                question=payload.question,
                conversation_id=payload.conversation_id,
                top_k=payload.top_k,
            ),
            media_type="text/event-stream",
        )
    return await service.ask(
        user=current_user,
        question=payload.question,
        conversation_id=payload.conversation_id,
        top_k=payload.top_k,
    )
