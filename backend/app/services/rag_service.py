from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.metrics import AI_EVALUATION_SCORE, AI_TOKENS, CACHE_EVENTS
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.usage_repository import UsageRepository
from app.schemas.chat import AskResponse, Citation
from app.schemas.document import SearchResult
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.vector_store import VectorStore


class RagService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        redis: Redis | None = None,
        embeddings: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
        llm: LLMService | None = None,
    ) -> None:
        self.session = session
        self.redis = redis
        self.embeddings = embeddings or EmbeddingService()
        self.vector_store = vector_store or VectorStore()
        self.llm = llm or LLMService()
        self.conversations = ConversationRepository(session)
        self.usage = UsageRepository(session)

    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        cache_key = f"semantic:{query}:{top_k}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                CACHE_EVENTS.labels("hit").inc()
                return [SearchResult.model_validate(item) for item in json.loads(cached)]
        query_vector = await self.embeddings.embed_query(query)
        results = await self.vector_store.search(query_vector, top_k)
        if self.redis:
            await self.redis.setex(
                cache_key,
                120,
                json.dumps([result.model_dump() for result in results]),
            )
            CACHE_EVENTS.labels("miss").inc()
        return results

    async def ask(
        self,
        *,
        user: User,
        question: str,
        conversation_id: str | None,
        top_k: int,
    ) -> AskResponse:
        conversation = None
        memory: list[tuple[str, str]] = []
        if conversation_id:
            conversation = await self.conversations.get_for_user(conversation_id, user.id)
            if conversation is not None:
                memory = [
                    (message.role, message.content)
                    for message in sorted(conversation.messages, key=lambda item: item.created_at)
                ]
        if conversation is None:
            conversation = await self.conversations.create(user.id, title=question[:80])
        await self.conversations.add_message(
            conversation_id=conversation.id,
            role="user",
            content=question,
        )
        context = await self.search(question, top_k)
        llm_response = await self.llm.answer(question=question, context=context, memory=memory)
        citations = [
            Citation(
                document_id=item.document_id,
                chunk_id=item.chunk_id,
                title=item.title,
                score=item.score,
            )
            for item in context
        ]
        evaluation_score = self._score_answer(llm_response.answer, context)
        await self.conversations.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=llm_response.answer,
            citations=[citation.model_dump() for citation in citations],
            prompt_tokens=llm_response.prompt_tokens,
            completion_tokens=llm_response.completion_tokens,
            evaluation_score=evaluation_score,
        )
        await self.usage.record(
            user_id=user.id,
            event_type="ask",
            prompt_tokens=llm_response.prompt_tokens,
            completion_tokens=llm_response.completion_tokens,
        )
        AI_TOKENS.labels("prompt").inc(llm_response.prompt_tokens)
        AI_TOKENS.labels("completion").inc(llm_response.completion_tokens)
        AI_EVALUATION_SCORE.set(evaluation_score)
        await self.session.commit()
        return AskResponse(
            conversation_id=conversation.id,
            answer=llm_response.answer,
            citations=citations,
            retrieved_context=context,
            prompt_tokens=llm_response.prompt_tokens,
            completion_tokens=llm_response.completion_tokens,
            evaluation_score=evaluation_score,
        )

    async def stream(
        self,
        *,
        user: User,
        question: str,
        conversation_id: str | None,
        top_k: int,
    ) -> AsyncGenerator[str, None]:
        response = await self.ask(
            user=user,
            question=question,
            conversation_id=conversation_id,
            top_k=top_k,
        )
        for word in response.answer.split():
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
        yield f"data: {json.dumps({'done': True, 'citations': [c.model_dump() for c in response.citations]})}\n\n"

    def _score_answer(self, answer: str, context: list[SearchResult]) -> float:
        if not context:
            return 0.0
        answer_terms = set(answer.lower().split())
        context_terms = set(" ".join(item.content for item in context).lower().split())
        overlap = len(answer_terms & context_terms) / max(1, len(answer_terms))
        source_factor = min(1.0, len(context) / 5)
        return round((0.65 * overlap) + (0.35 * source_factor), 3)
