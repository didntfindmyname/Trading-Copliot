from __future__ import annotations

import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.repositories.usage_repository import UsageRepository
from app.services.chunking import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.extraction import extract_upload
from app.services.vector_store import VectorStore


class DocumentService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        chunker: TextChunker | None = None,
        embeddings: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.session = session
        self.documents = DocumentRepository(session)
        self.usage = UsageRepository(session)
        self.chunker = chunker or TextChunker()
        self.embeddings = embeddings or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    async def upload(self, *, user: User, file: UploadFile, title: str | None) -> Document:
        extracted = await extract_upload(file)
        document = await self.documents.create(
            owner_id=user.id,
            title=title or file.filename or "Untitled",
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            size_bytes=extracted.size_bytes,
            checksum=extracted.checksum,
            content=extracted.content,
        )
        await self.usage.record(user_id=user.id, event_type="document_upload")
        await self.session.commit()
        return document

    async def index(self, document_id: str) -> Document:
        document = await self.documents.get(document_id)
        if document is None:
            raise ValueError("Document not found")
        await self.documents.mark_indexing(document)
        await self.session.commit()
        chunks = self.chunker.chunk(document.content)
        chunk_ids = [str(uuid.uuid4()) for _ in chunks]
        vectors = await self.embeddings.embed_texts(chunks)
        payloads = [
            {
                "chunk_id": chunk_id,
                "document_id": document.id,
                "title": document.title,
                "filename": document.filename,
                "content": chunk,
                "ordinal": ordinal,
            }
            for ordinal, (chunk_id, chunk) in enumerate(zip(chunk_ids, chunks, strict=True))
        ]
        await self.vector_store.upsert_chunks(
            vectors=vectors, chunk_ids=chunk_ids, payloads=payloads
        )
        await self.documents.replace_chunks(
            document,
            [
                (chunk_id, chunk, len(chunk.split()))
                for chunk_id, chunk in zip(chunk_ids, chunks, strict=True)
            ],
        )
        await self.session.commit()
        return document
