from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent
from app.agents.orchestrator import OrchestratorAgent
from app.orchestration.routing import RequestRouter
from app.orchestration.state import AgentState


class FakeResearchAgent(BaseAgent):
    name = "research"

    async def run(self, state: AgentState) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            output=f"Retrieved context for: {state.original_request}",
            success=True,
        )


class FakeSqlAgent(BaseAgent):
    name = "sql"

    async def run(self, state: AgentState) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            output="Executed read-only analytical query.",
            success=True,
        )


async def test_router_selects_parallel_agents_for_mixed_quant_request() -> None:
    route = RequestRouter().route(
        "Analyze the volatility incident using documents and compare historical latency"
    )

    assert route.mode == "parallel"
    assert route.agents == ["research", "sql"]


async def test_orchestrator_runs_injected_agents_and_evaluator_passes() -> None:
    orchestrator = OrchestratorAgent(
        agents={
            "research": FakeResearchAgent(),
            "sql": FakeSqlAgent(),
        }
    )

    result = await orchestrator.run(
        "Analyze the volatility incident using documents and compare historical latency"
    )

    assert result.state.outcome == "success"
    assert result.evaluation.passed is True
    assert result.state.completed_steps == ["research", "sql"]
    assert "Retrieved context" in (result.state.final_answer or "")
    assert result.state.tool_results == []


async def test_orchestrator_reports_missing_phase_two_agent_without_fabricating_work() -> None:
    result = await OrchestratorAgent().run("Generate Python code to inspect a traceback")

    assert result.state.outcome == "failed"
    assert result.evaluation.passed is False
    assert result.state.completed_steps == []
    assert "not implemented in Phase 1" in result.agent_results[0].error
    assert "No tool calls were executed" in (result.state.final_answer or "")
