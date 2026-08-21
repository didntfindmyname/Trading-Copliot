from __future__ import annotations

from pydantic import BaseModel, Field

from app.orchestration.routing import AgentName, ExecutionMode
from app.orchestration.state import AgentOutcome, ToolInvocationRecord
from app.schemas.chat import Citation


class AgentRunRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)


class AgentExecutionRead(BaseModel):
    agent_name: str
    success: bool
    latency_ms: float
    output: str
    error: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class AgentEvaluationRead(BaseModel):
    score: float
    passed: bool
    findings: list[str] = Field(default_factory=list)


class AgentRunResponse(BaseModel):
    trace_id: str
    outcome: AgentOutcome
    answer: str
    selected_agents: list[AgentName]
    execution_mode: ExecutionMode
    execution_plan: list[str]
    completed_steps: list[str]
    agent_results: list[AgentExecutionRead]
    tool_calls: list[ToolInvocationRecord]
    citations: list[Citation]
    evaluation: AgentEvaluationRead
    latency_ms: float
