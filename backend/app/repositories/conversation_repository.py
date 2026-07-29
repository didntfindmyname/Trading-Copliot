from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_for_user(self, conversation_id: str, user_id: str) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: str, title: str) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title[:255])
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def list_for_user(
        self, user_id: str, limit: int, offset: int
    ) -> tuple[list[Conversation], int]:
        result = await self.session.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        all_ids = await self.session.execute(
            select(Conversation.id).where(Conversation.user_id == user_id)
        )
        return list(result.scalars().all()), len(all_ids.scalars().all())

    async def add_message(
        self,
        *,
        conversation_id: str,
        role: str,
        content: str,
        citations: list[dict[str, object]] | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        evaluation_score: float = 0.0,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations=citations or [],
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            evaluation_score=evaluation_score,
        )
        self.session.add(message)
        await self.session.flush()
        return message
