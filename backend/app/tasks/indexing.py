from __future__ import annotations

import asyncio

from app.db.session import AsyncSessionLocal
from app.services.document_service import DocumentService
from app.tasks.worker import celery_app


def enqueue_index_document(document_id: str) -> None:
    index_document.delay(document_id)


@celery_app.task(name="documents.index")  # type: ignore[untyped-decorator]
def index_document(document_id: str) -> str:
    asyncio.run(_index_document(document_id))
    return document_id


async def _index_document(document_id: str) -> None:
    async with AsyncSessionLocal() as session:
        await DocumentService(session).index(document_id)
