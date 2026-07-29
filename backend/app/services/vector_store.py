from __future__ import annotations

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.core.config import settings
from app.schemas.document import SearchResult


class VectorStore:
    def __init__(self) -> None:
        self.client = AsyncQdrantClient(url=str(settings.qdrant_url))
        self.collection = settings.qdrant_collection

    async def ensure_collection(self, dimensions: int) -> None:
        collections = await self.client.get_collections()
        exists = any(collection.name == self.collection for collection in collections.collections)
        if exists:
            return
        await self.client.create_collection(
            collection_name=self.collection,
            vectors_config=models.VectorParams(size=dimensions, distance=models.Distance.COSINE),
        )

    async def upsert_chunks(
        self,
        *,
        vectors: list[list[float]],
        chunk_ids: list[str],
        payloads: list[dict[str, object]],
    ) -> None:
        if not vectors:
            return
        await self.ensure_collection(len(vectors[0]))
        points = [
            models.PointStruct(id=chunk_id, vector=vector, payload=payload)
            for chunk_id, vector, payload in zip(chunk_ids, vectors, payloads, strict=True)
        ]
        await self.client.upsert(collection_name=self.collection, points=points)

    async def search(self, query_vector: list[float], limit: int) -> list[SearchResult]:
        await self.ensure_collection(len(query_vector))
        response = await self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )
        output: list[SearchResult] = []
        for point in response.points:
            payload = point.payload or {}
            output.append(
                SearchResult(
                    document_id=str(payload.get("document_id", "")),
                    chunk_id=str(payload.get("chunk_id", point.id)),
                    title=str(payload.get("title", "Untitled")),
                    filename=str(payload.get("filename", "")),
                    content=str(payload.get("content", "")),
                    score=float(point.score),
                    ordinal=int(payload.get("ordinal", 0)),
                )
            )
        return output
