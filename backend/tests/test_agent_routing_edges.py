from __future__ import annotations

from app.orchestration.routing import RequestRouter


def test_router_does_not_match_keywords_inside_other_words() -> None:
    route = RequestRouter().route("Generate a safe read-only query for the latest incident rows")

    assert route.agents == ["sql"]
    assert route.mode == "sequential"


def test_router_keeps_python_latency_log_work_in_code_agent() -> None:
    route = RequestRouter().route("Write Python code to parse a latency log and compute p95")

    assert route.agents == ["code"]
    assert route.mode == "sequential"
    assert route.rationale == "Selected code agent for the request."


def test_router_recognizes_plural_documents_for_research_agent() -> None:
    route = RequestRouter().route(
        "Search documents, then run a SQL query to validate whether incident latency increased"
    )

    assert route.agents == ["research", "sql"]
    assert route.mode == "parallel"
    assert route.rationale == "Selected research, sql agents for the request."
