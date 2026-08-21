from __future__ import annotations

from pydantic import BaseModel, Field

from app.agents.base import AgentResult
from app.orchestration.state import AgentState


class EvaluationResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    findings: list[str] = Field(default_factory=list)


class EvaluatorAgent:
    name = "evaluator"

    async def evaluate(self, state: AgentState, results: list[AgentResult]) -> EvaluationResult:
        findings: list[str] = []
        successful_results = [result for result in results if result.success]

        if not successful_results:
            findings.append("No specialized agent completed successfully.")
        if any(result.error for result in results):
            findings.append("One or more agent executions returned an error.")
        if state.citations and not any("[" in result.output for result in successful_results):
            findings.append("Citations were retrieved but not referenced in the output.")

        coverage = len(successful_results) / max(1, len(results))
        score = round(coverage - (0.2 * len(findings)), 3)
        score = max(0.0, min(1.0, score))
        return EvaluationResult(score=score, passed=score >= 0.7, findings=findings)
