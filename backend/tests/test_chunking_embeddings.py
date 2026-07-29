from __future__ import annotations

from app.services.chunking import TextChunker
from app.services.embedding_service import EmbeddingService


async def test_chunker_uses_overlap() -> None:
    text = " ".join(f"token{i}" for i in range(25))
    chunks = TextChunker(max_words=10, overlap_words=2).chunk(text)
    assert len(chunks) == 3
    assert chunks[1].startswith("token8")


async def test_local_embeddings_are_normalized() -> None:
    vector = await EmbeddingService().embed_query("market data ingestion recovery")
    norm = sum(value * value for value in vector) ** 0.5
    assert 0.99 < norm < 1.01
