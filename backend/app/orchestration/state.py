from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.chat import Citation

AgentStepStatus = Literal["pending", "running", "completed", "failed", "skipped"]
AgentOutcome = Literal["success", "partial", "failed"]


class ToolInvocationRecord(BaseModel):
    agent_name: str
    tool_name: str
    arguments: dict[str, object] = Field(default_factory=dict)
    latency_ms: float = 0.0
    success: bool
    result_metadata: dict[str, object] = Field(default_factory=dict)
    error: str | None = None


class AgentStep(BaseModel):
    agent_name: str
    status: AgentStepStatus = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    latency_ms: float = 0.0
    output: str | None = None
    error: str | None = None


class AgentState(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    original_request: str
    execution_plan: list[str] = Field(default_factory=list)
    completed_steps: list[str] = Field(default_factory=list)
    intermediate_outputs: dict[str, object] = Field(default_factory=dict)
    tool_results: list[ToolInvocationRecord] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    retry_count: int = 0
    citations: list[Citation] = Field(default_factory=list)
    final_answer: str | None = None
    outcome: AgentOutcome = "partial"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def mark_updated(self) -> None:
        self.updated_at = datetime.now(UTC)
