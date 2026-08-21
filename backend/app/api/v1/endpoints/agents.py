from __future__ import annotations

from fastapi import APIRouter, Depends

from app.agents.orchestrator import OrchestratorAgent
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.agent import (
    AgentEvaluationRead,
    AgentExecutionRead,
    AgentRunRequest,
    AgentRunResponse,
)

router = APIRouter()


@router.post("/run", response_model=AgentRunResponse)
async def run_agents(
    payload: AgentRunRequest,
    current_user: User = Depends(get_current_user),
) -> AgentRunResponse:
    _ = current_user
    result = await OrchestratorAgent().run(payload.question)
    return AgentRunResponse(
        trace_id=result.state.trace_id,
        outcome=result.state.outcome,
        answer=result.state.final_answer or "",
        selected_agents=result.route.agents,
        execution_mode=result.route.mode,
        execution_plan=result.state.execution_plan,
        completed_steps=result.state.completed_steps,
        agent_results=[
            AgentExecutionRead(
                agent_name=agent_result.agent_name,
                success=agent_result.success,
                latency_ms=agent_result.latency_ms,
                output=agent_result.output,
                error=agent_result.error,
                metadata=agent_result.metadata,
            )
            for agent_result in result.agent_results
        ],
        tool_calls=result.state.tool_results,
        citations=result.state.citations,
        evaluation=AgentEvaluationRead(
            score=result.evaluation.score,
            passed=result.evaluation.passed,
            findings=result.evaluation.findings,
        ),
        latency_ms=result.latency_ms,
    )
