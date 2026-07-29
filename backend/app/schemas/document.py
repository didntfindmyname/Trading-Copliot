from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: str
    title: str
    filename: str
    content_type: str
    size_bytes: int
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SearchResult(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    filename: str
    content: str
    score: float
    ordinal: int


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
