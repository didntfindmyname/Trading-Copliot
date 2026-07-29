from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.document import SearchResult
from app.services.llm_service import LLMResponse
from app.services.rag_service import RagService


class FakeEmbeddings:
    async def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0]


class FakeVectorStore:
    async def search(self, query_vector: list[float], limit: int) -> list[SearchResult]:
        return [
            SearchResult(
                document_id="doc-1",
                chunk_id="chunk-1",
                title="Ops Runbook",
                filename="ops.md",
                content="Restart the ingestion worker after checking the exchange heartbeat.",
                score=0.93,
                ordinal=0,
            )
        ]


class FakeLLM:
    async def answer(
        self,
        *,
        question: str,
        context: list[SearchResult],
        memory: list[tuple[str, str]],
    ) -> LLMResponse:
        return LLMResponse(
            answer="Check heartbeat, then restart the ingestion worker. [1]",
            prompt_tokens=20,
            completion_tokens=10,
        )


async def test_rag_records_conversation_and_usage(session: AsyncSession) -> None:
    user = User(
        email="dev@athena.local",
        full_name="Dev",
        hashed_password="hashed",
        role="developer",
    )
    session.add(user)
    await session.commit()

    service = RagService(
        session,
        embeddings=FakeEmbeddings(),  # type: ignore[arg-type]
        vector_store=FakeVectorStore(),  # type: ignore[arg-type]
        llm=FakeLLM(),  # type: ignore[arg-type]
    )
    response = await service.ask(
        user=user,
        question="How do I recover ingestion?",
        conversation_id=None,
        top_k=1,
    )

    assert response.answer.startswith("Check heartbeat")
    assert response.citations[0].title == "Ops Runbook"
    assert response.prompt_tokens == 20
