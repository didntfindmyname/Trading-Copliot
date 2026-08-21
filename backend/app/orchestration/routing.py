from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

AgentName = Literal["research", "sql", "code"]
ExecutionMode = Literal["sequential", "parallel"]


class AgentRoute(BaseModel):
    agents: list[AgentName] = Field(default_factory=list)
    mode: ExecutionMode = "sequential"
    rationale: str


class RequestRouter:
    sql_keywords = {
        "sql",
        "query",
        "database",
        "postgresql",
        "table",
        "tables",
        "schema",
        "latency",
        "historical",
        "signal",
        "signals",
    }
    code_keywords = {
        "code",
        "python",
        "function",
        "bug",
        "fix",
        "test",
        "traceback",
        "exception",
    }
    research_keywords = {
        "document",
        "documents",
        "docs",
        "source",
        "sources",
        "citation",
        "citations",
        "runbook",
        "research",
        "knowledge",
    }
    research_phrases = {
        "knowledge base",
        "source material",
        "source-backed",
        "cite each source",
        "with citations",
    }

    def route(self, request: str) -> AgentRoute:
        normalized = request.lower()
        tokens = set(re.findall(r"[a-z0-9-]+", normalized))
        agents: list[AgentName] = []
        if self._matches(normalized, tokens, self.research_keywords, self.research_phrases):
            agents.append("research")
        if self._matches(normalized, tokens, self.sql_keywords):
            agents.append("sql")
        if self._matches(normalized, tokens, self.code_keywords):
            agents.append("code")
        if "code" in agents and "sql" in agents and "log" in tokens:
            strong_sql_tokens = {"sql", "query", "database", "postgresql", "table", "tables", "schema"}
            if not strong_sql_tokens & tokens:
                agents.remove("sql")
        if not agents:
            agents.append("research")

        mode: ExecutionMode = "parallel" if len(agents) > 1 else "sequential"
        rationale = f"Selected {', '.join(agents)} agent path for the request."
        return AgentRoute(agents=agents, mode=mode, rationale=rationale)

    def _matches(
        self,
        text: str,
        tokens: set[str],
        keywords: set[str],
        phrases: set[str] | None = None,
    ) -> bool:
        if keywords & tokens:
            return True
        return any(phrase in text for phrase in phrases or set())
