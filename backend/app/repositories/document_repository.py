from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        owner_id: str,
        title: str,
        filename: str,
        content_type: str,
        size_bytes: int,
        checksum: str,
        content: str,
    ) -> Document:
        document = Document(
            owner_id=owner_id,
            title=title,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            checksum=checksum,
            content=content,
            status="uploaded",
        )
        self.session.add(document)
        await self.session.flush()
        return document

    async def get(self, document_id: str) -> Document | None:
        return await self.session.get(Document, document_id)

    async def get_with_chunks(self, document_id: str) -> Document | None:
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: str, limit: int, offset: int
    ) -> tuple[list[Document], int]:
        statement = (
            select(Document)
            .where(Document.owner_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        count_statement = select(func.count(Document.id)).where(Document.owner_id == user_id)
        documents = (await self.session.execute(statement)).scalars().all()
        total = (await self.session.execute(count_statement)).scalar_one()
        return list(documents), int(total)

    async def replace_chunks(self, document: Document, chunks: list[tuple[str, str, int]]) -> None:
        await self.session.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document.id)
        )
        for ordinal, (chunk_id, content, token_count) in enumerate(chunks):
            self.session.add(
                DocumentChunk(
                    id=chunk_id,
                    document_id=document.id,
                    ordinal=ordinal,
                    content=content,
                    token_count=token_count,
                    qdrant_point_id=chunk_id,
                )
            )
        document.chunk_count = len(chunks)
        document.status = "indexed"
        await self.session.flush()

    async def mark_indexing(self, document: Document) -> None:
        document.status = "indexing"
        await self.session.flush()

    async def mark_failed(self, document: Document) -> None:
        document.status = "failed"
        await self.session.flush()
