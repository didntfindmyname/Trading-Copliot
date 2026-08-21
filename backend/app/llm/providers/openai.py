from __future__ import annotations

import json

import httpx

from app.core.config import settings
from app.llm.base import ChatMessage, LLMProvider, LLMResult, LLMToolCall, ToolDefinition


class OpenAIChatProvider(LLMProvider):
    provider_name = "openai"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.openai_api_key

    async def generate(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        timeout_seconds: float = 60.0,
    ) -> LLMResult:
        return await self._post_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            timeout_seconds=timeout_seconds,
        )

    async def generate_with_tools(
        self,
        *,
        messages: list[ChatMessage],
        tools: list[ToolDefinition],
        model: str | None = None,
        temperature: float = 0.2,
        timeout_seconds: float = 60.0,
    ) -> LLMResult:
        openai_tools: list[dict[str, object]] = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema or {"type": "object", "properties": {}},
                },
            }
            for tool in tools
        ]
        return await self._post_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            timeout_seconds=timeout_seconds,
            tools=openai_tools,
        )

    async def _post_chat_completion(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None,
        temperature: float,
        timeout_seconds: float,
        tools: list[dict[str, object]] | None = None,
    ) -> LLMResult:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required when llm_provider=openai")

        payload: dict[str, object] = {
            "model": model or settings.openai_model,
            "messages": [message.model_dump() for message in messages],
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            body = response.json()

        usage = body.get("usage", {})
        choice = body["choices"][0]["message"]
        tool_calls = []
        for raw_call in choice.get("tool_calls") or []:
            function = raw_call.get("function", {})
            try:
                arguments = json.loads(function.get("arguments") or "{}")
            except json.JSONDecodeError:
                arguments = {"_malformed_arguments": function.get("arguments")}
            tool_calls.append(
                LLMToolCall(
                    tool_name=function.get("name", ""),
                    arguments=arguments,
                )
            )

        return LLMResult(
            content=choice.get("content") or "",
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            tool_calls=tool_calls,
            model=str(payload["model"]),
            provider=self.provider_name,
        )
