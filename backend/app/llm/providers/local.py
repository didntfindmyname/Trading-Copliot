from __future__ import annotations

from app.llm.base import ChatMessage, LLMProvider, LLMResult, LLMToolCall, ToolDefinition


class LocalLLMProvider(LLMProvider):
    provider_name = "local"

    async def generate(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        timeout_seconds: float = 60.0,
    ) -> LLMResult:
        _ = temperature, timeout_seconds
        prompt = "\n".join(message.content for message in messages)
        last_user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            prompt,
        )
        content = (
            "Local LLM provider response. Configure an external provider for generated model "
            f"answers. Request summary: {last_user_message[:700]}"
        )
        return LLMResult(
            content=content,
            prompt_tokens=self._estimate_tokens(prompt),
            completion_tokens=self._estimate_tokens(content),
            model=model or "local-heuristic",
            provider=self.provider_name,
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
        result = await self.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            timeout_seconds=timeout_seconds,
        )
        request_text = " ".join(message.content.lower() for message in messages)
        selected = [
            LLMToolCall(tool_name=tool.name, arguments={})
            for tool in tools
            if any(token in request_text for token in tool.name.lower().split("_"))
        ][:1]
        return result.model_copy(update={"tool_calls": selected})

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()) * 4 // 3)
