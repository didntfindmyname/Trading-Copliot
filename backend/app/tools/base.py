from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.tools.schemas import ToolExecutionEnvelope, ToolExecutionMetadata

InputModel = TypeVar("InputModel", bound=BaseModel)
OutputModel = TypeVar("OutputModel", bound=BaseModel)


class Tool(Generic[InputModel, OutputModel], ABC):
    name: str
    description: str
    input_model: type[InputModel]

    async def run(self, *, payload: dict[str, Any], agent_name: str) -> ToolExecutionEnvelope:
        start = datetime.now(UTC)
        timer = time.perf_counter()
        trace_id = payload.get("trace_id") if isinstance(payload.get("trace_id"), str) else None
        try:
            validated = self.input_model.model_validate(payload)
            output = await self.execute(validated)
            end = datetime.now(UTC)
            return ToolExecutionEnvelope(
                metadata=ToolExecutionMetadata(
                    tool_name=self.name,
                    agent_name=agent_name,
                    arguments=validated.model_dump(mode="json"),
                    start_time=start,
                    end_time=end,
                    latency_ms=round((time.perf_counter() - timer) * 1000, 3),
                    success=True,
                    trace_id=trace_id,
                ),
                result=output.model_dump(mode="json"),
            )
        except Exception as exc:
            end = datetime.now(UTC)
            return ToolExecutionEnvelope(
                metadata=ToolExecutionMetadata(
                    tool_name=self.name,
                    agent_name=agent_name,
                    arguments=dict(payload),
                    start_time=start,
                    end_time=end,
                    latency_ms=round((time.perf_counter() - timer) * 1000, 3),
                    success=False,
                    error_type=type(exc).__name__,
                    trace_id=trace_id,
                ),
                error=str(exc),
            )

    @abstractmethod
    async def execute(self, payload: InputModel) -> OutputModel:
        raise NotImplementedError
