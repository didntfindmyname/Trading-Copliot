from __future__ import annotations

from collections.abc import AsyncGenerator

from app.core.config import settings
from app.llm import ChatMessage, LLMProvider
from app.llm.factory import build_llm_provider
from app.schemas.document import SearchResult


class LLMResponse:
    def __init__(self, answer: str, prompt_tokens: int, completion_tokens: int) -> None:
        self.answer = answer
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class LLMService:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or build_llm_provider()

    async def answer(
        self,
        *,
        question: str,
        context: list[SearchResult],
        memory: list[tuple[str, str]],
    ) -> LLMResponse:
        prompt = self._render_prompt(question=question, context=context, memory=memory)
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return await self._answer_provider(prompt)
        answer = self._answer_local(question=question, context=context, memory=memory)
        return LLMResponse(
            answer=answer,
            prompt_tokens=self._estimate_tokens(prompt),
            completion_tokens=self._estimate_tokens(answer),
        )

    async def stream_answer(
        self,
        *,
        question: str,
        context: list[SearchResult],
        memory: list[tuple[str, str]],
    ) -> AsyncGenerator[str, None]:
        response = await self.answer(question=question, context=context, memory=memory)
        for token in response.answer.split():
            yield f"{token} "

    def _render_prompt(
        self,
        *,
        question: str,
        context: list[SearchResult],
        memory: list[tuple[str, str]],
    ) -> str:
        sources = "\n".join(
            f"[{index}] {item.title} ({item.filename}) score={item.score:.3f}\n{item.content}"
            for index, item in enumerate(context, start=1)
        )
        prior = "\n".join(f"{role}: {content}" for role, content in memory[-6:])
        return (
            "You are Athena, an internal engineering copilot for a quantitative trading firm. "
            "Answer with operational precision, cite provided sources, and avoid unsupported claims.\n\n"
            f"Conversation memory:\n{prior or 'No prior turns.'}\n\n"
            f"Retrieved sources:\n{sources or 'No sources retrieved.'}\n\n"
            f"Question: {question}\nAnswer:"
        )

    async def _answer_provider(self, prompt: str) -> LLMResponse:
        result = await self.provider.generate(
            messages=[ChatMessage(role="user", content=prompt)],
            model=settings.openai_model,
            temperature=0.2,
            timeout_seconds=60,
        )
        return LLMResponse(
            answer=result.content,
            prompt_tokens=result.prompt_tokens or self._estimate_tokens(prompt),
            completion_tokens=result.completion_tokens,
        )

    def _answer_local(
        self,
        *,
        question: str,
        context: list[SearchResult],
        memory: list[tuple[str, str]],
    ) -> str:
        if not context:
            return (
                "I could not find indexed internal sources for that question. "
                "Upload or index the relevant runbook, code, or research note and ask again."
            )
        lead = context[0]
        supporting = ", ".join(f"{item.title} [{idx}]" for idx, item in enumerate(context[:4], 1))
        prior_hint = ""
        if memory:
            prior_hint = " I also considered the recent conversation context."
        return (
            f"Based on the strongest retrieved source, {lead.title}, the relevant detail is: "
            f"{lead.content[:700].strip()}{'...' if len(lead.content) > 700 else ''}\n\n"
            f"For traceability, compare the supporting sources: {supporting}.{prior_hint}\n\n"
            f"Question handled: {question}"
        )

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()) * 4 // 3)
