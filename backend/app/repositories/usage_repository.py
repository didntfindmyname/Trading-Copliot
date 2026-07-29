from __future__ import annotations

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk
from app.models.usage import UsageEvent
from app.models.user import User
from app.schemas.usage import AdminUsageSummary, UsageSummary


class UsageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(
        self,
        *,
        user_id: str,
        event_type: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cache_hit: bool = False,
    ) -> UsageEvent:
        event = UsageEvent(
            user_id=user_id,
            event_type=event_type,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cache_hit=cache_hit,
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def summarize_user(self, user_id: str) -> UsageSummary:
        result = await self.session.execute(
            select(
                func.coalesce(func.sum(UsageEvent.prompt_tokens), 0),
                func.coalesce(func.sum(UsageEvent.completion_tokens), 0),
                func.count(UsageEvent.id),
                func.coalesce(func.sum(cast(UsageEvent.cache_hit, Integer)), 0),
            ).where(UsageEvent.user_id == user_id)
        )
        prompt, completion, requests, cache_hits = result.one()
        return UsageSummary(
            prompt_tokens=int(prompt),
            completion_tokens=int(completion),
            requests=int(requests),
            cache_hits=int(cache_hits),
        )

    async def summarize_admin(self) -> AdminUsageSummary:
        usage = await self.session.execute(
            select(
                func.coalesce(func.sum(UsageEvent.prompt_tokens), 0),
                func.coalesce(func.sum(UsageEvent.completion_tokens), 0),
                func.count(UsageEvent.id),
                func.coalesce(func.sum(cast(UsageEvent.cache_hit, Integer)), 0),
            )
        )
        prompt, completion, requests, cache_hits = usage.one()
        active_users = (await self.session.execute(select(func.count(User.id)))).scalar_one()
        documents = (
            await self.session.execute(
                select(func.count(Document.id)).where(Document.status == "indexed")
            )
        ).scalar_one()
        chunks = (await self.session.execute(select(func.count(DocumentChunk.id)))).scalar_one()
        return AdminUsageSummary(
            prompt_tokens=int(prompt),
            completion_tokens=int(completion),
            requests=int(requests),
            cache_hits=int(cache_hits),
            active_users=int(active_users),
            documents_indexed=int(documents),
            chunks_indexed=int(chunks),
        )
