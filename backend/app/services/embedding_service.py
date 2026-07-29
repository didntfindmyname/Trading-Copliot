from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence

import httpx

from app.core.config import settings


class EmbeddingService:
    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if settings.embedding_provider == "openai" and settings.openai_api_key:
            return await self._embed_openai(texts)
        return [self._embed_local(text) for text in texts]

    async def embed_query(self, text: str) -> list[float]:
        return (await self.embed_texts([text]))[0]

    async def _embed_openai(self, texts: Sequence[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.openai_embedding_model, "input": list(texts)},
            )
            response.raise_for_status()
            payload = response.json()
        return [item["embedding"] for item in payload["data"]]

    def _embed_local(self, text: str) -> list[float]:
        dimensions = settings.local_embedding_dimensions
        vector = [0.0] * dimensions
        tokens = [token.lower() for token in text.split()]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[idx] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
