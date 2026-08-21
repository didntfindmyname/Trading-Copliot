from __future__ import annotations

from app.core.config import settings
from app.llm.base import LLMProvider
from app.llm.providers import LocalLLMProvider, OpenAIChatProvider


def build_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        return OpenAIChatProvider()
    return LocalLLMProvider()
