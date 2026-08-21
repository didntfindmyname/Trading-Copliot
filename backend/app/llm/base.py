from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ToolDefinition(BaseModel):
    name: str = Field(min_length=1)
    description: str
    input_schema: dict[str, object] = Field(default_factory=dict)


class LLMToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, object] = Field(default_factory=dict)


class LLMResult(BaseModel):
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    model: str | None = None
    provider: str | None = None


class LLMProvider(ABC):
    provider_name: str

    @abstractmethod
    async def generate(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        timeout_seconds: float = 60.0,
    ) -> LLMResult:
        raise NotImplementedError

    @abstractmethod
    async def generate_with_tools(
        self,
        *,
        messages: list[ChatMessage],
        tools: list[ToolDefinition],
        model: str | None = None,
        temperature: float = 0.2,
        timeout_seconds: float = 60.0,
    ) -> LLMResult:
        raise NotImplementedError
