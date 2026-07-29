from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.document import SearchResult


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    conversation_id: str | None = None
    stream: bool = False
    top_k: int = Field(default=5, ge=1, le=12)


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    score: float


class AskResponse(BaseModel):
    conversation_id: str
    answer: str
    citations: list[Citation]
    retrieved_context: list[SearchResult]
    prompt_tokens: int
    completion_tokens: int
    evaluation_score: float


class MessageRead(BaseModel):
    id: str
    role: str
    content: str
    citations: list[dict[str, object]]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationRead(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageRead] = []

    model_config = {"from_attributes": True}
