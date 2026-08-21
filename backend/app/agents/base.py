from __future__ import annotations

import time
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from app.orchestration.state import AgentState
from app.schemas.chat import Citation


class AgentResult(BaseModel):
    agent_name: str
    output: str
    success: bool = True
    citations: list[Citation] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 0.0


class BaseAgent(ABC):
    name: str

    async def run_with_timing(self, state: AgentState) -> AgentResult:
        start = time.perf_counter()
        try:
            result = await self.run(state)
        except Exception as exc:
            result = AgentResult(
                agent_name=self.name,
                output="",
                success=False,
                error=str(exc),
            )
        result.latency_ms = round((time.perf_counter() - start) * 1000, 3)
        return result

    @abstractmethod
    async def run(self, state: AgentState) -> AgentResult:
        raise NotImplementedError
