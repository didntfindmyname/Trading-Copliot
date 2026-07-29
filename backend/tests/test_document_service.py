from __future__ import annotations

from io import BytesIO

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.document_service import DocumentService


class FakeVectorStore:
    def __init__(self) -> None:
        self.payloads: list[dict[str, object]] = []

    async def upsert_chunks(
        self,
        *,
        vectors: list[list[float]],
        chunk_ids: list[str],
        payloads: list[dict[str, object]],
    ) -> None:
        assert vectors
        assert chunk_ids
        self.payloads = payloads


async def test_document_upload_and_index(session: AsyncSession) -> None:
    user = User(
        email="researcher@athena.local",
        full_name="Researcher",
        hashed_password="hashed",
        role="researcher",
    )
    session.add(user)
    await session.commit()

    file = UploadFile(
        filename="runbook.md",
        file=BytesIO(b"# Runbook\nRestart ingestion from the committed offset."),
    )
    vector_store = FakeVectorStore()
    service = DocumentService(session, vector_store=vector_store)
    document = await service.upload(user=user, file=file, title="Runbook")
    indexed = await service.index(document.id)

    assert indexed.status == "indexed"
    assert indexed.chunk_count == 1
    assert vector_store.payloads[0]["title"] == "Runbook"
