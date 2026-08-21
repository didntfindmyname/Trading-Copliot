from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.document import SearchResult
from app.schemas.operations import OperationsSnapshot


class ToolExecutionMetadata(BaseModel):
    tool_name: str
    agent_name: str
    arguments: dict[str, object] = Field(default_factory=dict)
    start_time: datetime
    end_time: datetime
    latency_ms: float
    success: bool
    error_type: str | None = None
    trace_id: str | None = None


class ToolExecutionEnvelope(BaseModel):
    metadata: ToolExecutionMetadata
    result: dict[str, object] | None = None
    error: str | None = None


class SearchDocumentsInput(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=5, ge=1, le=12)
    trace_id: str | None = None


class SearchDocumentsOutput(BaseModel):
    query: str
    results: list[SearchResult]


class RetrieveDocumentInput(BaseModel):
    document_id: str = Field(min_length=1, max_length=80)
    include_chunks: bool = True
    max_content_chars: int = Field(default=4000, ge=200, le=20000)
    trace_id: str | None = None


class DocumentChunkRead(BaseModel):
    id: str
    ordinal: int
    content: str
    token_count: int


class RetrieveDocumentOutput(BaseModel):
    document_id: str
    title: str
    filename: str
    status: str
    content: str
    truncated: bool
    chunks: list[DocumentChunkRead] = Field(default_factory=list)


class GetDatabaseSchemaInput(BaseModel):
    table_names: list[str] | None = None
    trace_id: str | None = None


class DatabaseColumnSchema(BaseModel):
    name: str
    type: str
    nullable: bool


class DatabaseTableSchema(BaseModel):
    name: str
    columns: list[DatabaseColumnSchema]


class GetDatabaseSchemaOutput(BaseModel):
    tables: list[DatabaseTableSchema]


class RunSqlQueryInput(BaseModel):
    sql: str = Field(min_length=6, max_length=5000)
    row_limit: int = Field(default=100, ge=1, le=500)
    timeout_seconds: float = Field(default=5.0, gt=0.0, le=30.0)
    trace_id: str | None = None


class RunSqlQueryOutput(BaseModel):
    columns: list[str]
    rows: list[dict[str, object]]
    row_count: int
    truncated: bool


class SearchConversationMemoryInput(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    user_id: str | None = Field(default=None, max_length=80)
    limit: int = Field(default=5, ge=1, le=25)
    trace_id: str | None = None


class ConversationMemoryHit(BaseModel):
    conversation_id: str
    message_id: str
    role: str
    content: str
    created_at: datetime


class SearchConversationMemoryOutput(BaseModel):
    query: str
    results: list[ConversationMemoryHit]


class GetSystemMetricsInput(BaseModel):
    trace_id: str | None = None


class GetSystemMetricsOutput(BaseModel):
    snapshot: OperationsSnapshot


class ExecutePythonInput(BaseModel):
    code: str = Field(min_length=1, max_length=8000)
    timeout_seconds: float = Field(default=2.0, gt=0.0, le=5.0)
    max_output_chars: int = Field(default=4000, ge=200, le=20000)
    trace_id: str | None = None


class ExecutePythonOutput(BaseModel):
    stdout: str
    stderr: str
    return_code: int
    timed_out: bool
    safety_level: Literal["restricted-subprocess"]
