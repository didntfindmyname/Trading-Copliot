from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.agents.orchestrator import OrchestratorAgent  # noqa: E402
from app.orchestration.routing import RequestRouter  # noqa: E402

from eval.metrics import TaskResult, summarize  # noqa: E402

Mode = Literal["router", "orchestrator"]


class EvalTask(BaseModel):
    id: str
    category: str
    prompt: str = Field(min_length=3)
    expected_agents: list[str] = Field(min_length=1)
    expected_mode: Literal["sequential", "parallel"]


def load_tasks(path: Path) -> list[EvalTask]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [EvalTask.model_validate(item) for item in payload]


async def evaluate_tasks(tasks: list[EvalTask], mode: Mode) -> list[TaskResult]:
    if mode == "router":
        return [_evaluate_route(task) for task in tasks]
    return [await _evaluate_orchestrator(task) for task in tasks]


def _evaluate_route(task: EvalTask) -> TaskResult:
    router = RequestRouter()
    start = time.perf_counter()
    route = router.route(task.prompt)
    latency_ms = (time.perf_counter() - start) * 1000
    route_correct = set(route.agents) == set(task.expected_agents)
    mode_correct = route.mode == task.expected_mode
    return TaskResult(
        task_id=task.id,
        category=task.category,
        expected_agents=task.expected_agents,
        selected_agents=route.agents,
        expected_mode=task.expected_mode,
        selected_mode=route.mode,
        route_correct=route_correct,
        mode_correct=mode_correct,
        success=route_correct and mode_correct,
        latency_ms=latency_ms,
    )


async def _evaluate_orchestrator(task: EvalTask) -> TaskResult:
    start = time.perf_counter()
    try:
        run = await OrchestratorAgent().run(task.prompt)
        latency_ms = (time.perf_counter() - start) * 1000
        route_correct = set(run.route.agents) == set(task.expected_agents)
        mode_correct = run.route.mode == task.expected_mode
        return TaskResult(
            task_id=task.id,
            category=task.category,
            expected_agents=task.expected_agents,
            selected_agents=run.route.agents,
            expected_mode=task.expected_mode,
            selected_mode=run.route.mode,
            route_correct=route_correct,
            mode_correct=mode_correct,
            success=route_correct and mode_correct and run.state.outcome == "success",
            latency_ms=latency_ms,
            tool_calls=len(run.state.tool_results),
            outcome=run.state.outcome,
            evaluation_score=run.evaluation.score,
        )
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return TaskResult(
            task_id=task.id,
            category=task.category,
            expected_agents=task.expected_agents,
            selected_agents=[],
            expected_mode=task.expected_mode,
            selected_mode="sequential",
            route_correct=False,
            mode_correct=False,
            success=False,
            latency_ms=latency_ms,
            outcome="error",
            error=str(exc),
        )


def write_report(
    *,
    output_dir: Path,
    dataset: Path,
    mode: Mode,
    results: list[TaskResult],
    summary: dict[str, Any],
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = output_dir / f"{timestamp}-{mode}-report.json"
    md_path = output_dir / f"{timestamp}-{mode}-summary.md"
    report = {
        "created_at": datetime.now(UTC).isoformat(),
        "dataset": str(dataset),
        "mode": mode,
        "summary": summary,
        "results": [result.__dict__ for result in results],
        "notes": [
            "Metrics are measured locally against the current repository state.",
            "Token usage and inference cost are not reported in Phase 1 because no production agent model calls are made by the benchmark.",
            "Tool-call metrics are expected to remain zero until MCP/tool-backed agents are implemented.",
        ],
    }
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    return json_path, md_path


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# QuantOps Agent Evaluation Summary",
        "",
        f"- Created at: `{report['created_at']}`",
        f"- Dataset: `{report['dataset']}`",
        f"- Mode: `{report['mode']}`",
        f"- Tasks: `{summary['task_count']}`",
        f"- Success rate: `{summary['success_rate']:.2%}`",
        f"- Route accuracy: `{summary['route_accuracy']:.2%}`",
        f"- Mode accuracy: `{summary['mode_accuracy']:.2%}`",
        f"- Agent selection precision: `{summary['agent_selection_precision']:.2%}`",
        f"- Agent selection recall: `{summary['agent_selection_recall']:.2%}`",
        f"- Agent selection F1: `{summary['agent_selection_f1']:.2%}`",
        f"- Average latency: `{summary['avg_latency_ms']:.3f} ms`",
        f"- p50 latency: `{summary['p50_latency_ms']:.3f} ms`",
        f"- p95 latency: `{summary['p95_latency_ms']:.3f} ms`",
        f"- Average tool calls: `{summary['avg_tool_calls']}`",
        "",
        "## Category Breakdown",
        "",
    ]
    for category, values in summary["category_breakdown"].items():
        lines.append(
            f"- `{category}`: tasks={values['task_count']}, success={values['success_rate']:.2%}, "
            f"route={values['route_accuracy']:.2%}, latency={values['avg_latency_ms']:.3f} ms"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Token usage and inference cost are intentionally omitted in Phase 1.",
            "- Tool-call metrics are expected to remain zero until MCP/tool-backed agents land.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run QuantOps multi-agent evaluations.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--mode", choices=["router", "orchestrator"], default="router")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "eval" / "runs")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    tasks = load_tasks(args.dataset)
    results = await evaluate_tasks(tasks, args.mode)
    summary = summarize(results)
    json_path, md_path = write_report(
        output_dir=args.output_dir,
        dataset=args.dataset,
        mode=args.mode,
        results=results,
        summary=summary,
    )
    print(json.dumps(summary, indent=2))
    print(f"JSON report: {json_path}")
    print(f"Markdown summary: {md_path}")


if __name__ == "__main__":
    asyncio.run(main())
