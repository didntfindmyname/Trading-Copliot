from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.pagination import Page
from app.db.session import get_session
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentRead
from app.services.document_service import DocumentService
from app.tasks.indexing import enqueue_index_document

router = APIRouter()


@router.post("", response_model=DocumentRead, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> object:
    document = await DocumentService(session).upload(user=current_user, file=file, title=title)
    background_tasks.add_task(enqueue_index_document, document.id)
    return document


@router.get("", response_model=Page[DocumentRead])
async def list_documents(
    limit: int = 25,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Page[DocumentRead]:
    items, total = await DocumentRepository(session).list_for_user(current_user.id, limit, offset)
    return Page[DocumentRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/{document_id}/index", response_model=DocumentRead)
async def index_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> object:
    document = await DocumentRepository(session).get(document_id)
    if document is None or document.owner_id != current_user.id:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return await DocumentService(session).index(document_id)
