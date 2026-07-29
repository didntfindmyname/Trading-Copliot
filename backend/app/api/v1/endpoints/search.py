from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_redis
from app.db.session import get_session
from app.models.user import User
from app.schemas.document import SearchResponse
from app.services.rag_service import RagService

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search_documents(
    query: str = Query(min_length=2, max_length=500),
    top_k: int = Query(default=5, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> SearchResponse:
    _ = current_user
    results = await RagService(session, redis=redis).search(query, top_k)
    return SearchResponse(query=query, results=results)
