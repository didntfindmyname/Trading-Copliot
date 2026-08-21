from __future__ import annotations

import asyncio
import time

import structlog

from app.agents.base import AgentResult, BaseAgent
from app.agents.evaluator_agent import EvaluationResult, EvaluatorAgent
from app.core.config import settings
from app.orchestration.routing import AgentName, AgentRoute, RequestRouter
from app.orchestration.state import AgentState

logger = structlog.get_logger(__name__)


class OrchestratorRunResult:
    def __init__(
        self,
        *,
        state: AgentState,
        route: AgentRoute,
        agent_results: list[AgentResult],
        evaluation: EvaluationResult,
        latency_ms: float,
    ) -> None:
        self.state = state
        self.route = route
        self.agent_results = agent_results
        self.evaluation = evaluation
        self.latency_ms = latency_ms


class OrchestratorAgent:
    name = "orchestrator"

    def __init__(
        self,
        *,
        router: RequestRouter | None = None,
        evaluator: EvaluatorAgent | None = None,
        agents: dict[AgentName, BaseAgent] | None = None,
    ) -> None:
        self.router = router or RequestRouter()
        self.evaluator = evaluator or EvaluatorAgent()
        self.agents = agents or {}

    async def run(self, request: str) -> OrchestratorRunResult:
        start = time.perf_counter()
        state = AgentState(original_request=request)
        route = self.router.route(request)
        state.execution_plan = [
            f"Route request to {agent_name} agent" for agent_name in route.agents
        ]

        logger.info(
            "agent_orchestration_started",
            trace_id=state.trace_id,
            agents=route.agents,
            mode=route.mode,
        )

        try:
            agent_results = await asyncio.wait_for(
                self._run_agents(route, state),
                timeout=settings.agent_request_timeout_seconds,
            )
        except TimeoutError:
            state.errors.append("Agent orchestration timed out.")
            agent_results = [
                AgentResult(
                    agent_name=self.name,
                    output="",
                    success=False,
                    error="Agent orchestration timed out.",
                )
            ]

        for result in agent_results:
            if result.success:
                state.completed_steps.append(result.agent_name)
                state.intermediate_outputs[result.agent_name] = result.output
                state.citations.extend(result.citations)
            elif result.error:
                state.errors.append(f"{result.agent_name}: {result.error}")

        evaluation = await self.evaluator.evaluate(state, agent_results)
        state.final_answer = self._compose_final_answer(route, agent_results, evaluation)
        state.outcome = "success" if evaluation.passed else "partial"
        if not any(result.success for result in agent_results):
            state.outcome = "failed"
        state.mark_updated()
        latency_ms = round((time.perf_counter() - start) * 1000, 3)

        logger.info(
            "agent_orchestration_completed",
            trace_id=state.trace_id,
            outcome=state.outcome,
            evaluation_score=evaluation.score,
            latency_ms=latency_ms,
        )
        return OrchestratorRunResult(
            state=state,
            route=route,
            agent_results=agent_results,
            evaluation=evaluation,
            latency_ms=latency_ms,
        )

    async def _run_agents(self, route: AgentRoute, state: AgentState) -> list[AgentResult]:
        runnable_agents = [self.agents[name] for name in route.agents if name in self.agents]
        missing_agents = [name for name in route.agents if name not in self.agents]
        missing_results = [
            AgentResult(
                agent_name=name,
                output="",
                success=False,
                error=(
                    f"{name} agent is planned but not implemented in Phase 1. "
                    "Install the specialized agent in Phase 2."
                ),
            )
            for name in missing_agents
        ]
        if not runnable_agents:
            return missing_results

        if route.mode == "parallel":
            results = await asyncio.gather(
                *(agent.run_with_timing(state) for agent in runnable_agents)
            )
        else:
            results = []
            for agent in runnable_agents[: settings.max_agent_iterations]:
                results.append(await agent.run_with_timing(state))
        return [*results, *missing_results]

    def _compose_final_answer(
        self,
        route: AgentRoute,
        results: list[AgentResult],
        evaluation: EvaluationResult,
    ) -> str:
        successful = [result for result in results if result.success]
        if not successful:
            return (
                "I created an execution plan, but no specialized Phase 2 agent is available "
                f"yet for this route: {', '.join(route.agents)}. No tool calls were executed."
            )
        outputs = "\n\n".join(result.output for result in successful)
        critic_note = ""
        if evaluation.findings:
            critic_note = "\n\nEvaluator notes: " + " ".join(evaluation.findings)
        return f"{outputs}{critic_note}"
