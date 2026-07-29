from __future__ import annotations

from pydantic import BaseModel


class UsageSummary(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    requests: int
    cache_hits: int


class AdminUsageSummary(UsageSummary):
    active_users: int
    documents_indexed: int
    chunks_indexed: int
