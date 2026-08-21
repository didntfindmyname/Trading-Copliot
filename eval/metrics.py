from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import ceil
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class TaskResult:
    task_id: str
    category: str
    expected_agents: list[str]
    selected_agents: list[str]
    expected_mode: str
    selected_mode: str
    route_correct: bool
    mode_correct: bool
    success: bool
    latency_ms: float
    tool_calls: int = 0
    outcome: str | None = None
    evaluation_score: float | None = None
    error: str | None = None


def summarize(results: list[TaskResult]) -> dict[str, Any]:
    if not results:
        return {
            "task_count": 0,
            "success_rate": 0.0,
            "route_accuracy": 0.0,
            "mode_accuracy": 0.0,
            "agent_selection_precision": 0.0,
            "agent_selection_recall": 0.0,
            "agent_selection_f1": 0.0,
            "avg_tool_calls": 0.0,
            "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "category_breakdown": {},
            "outcome_counts": {},
        }

    true_positive = 0
    false_positive = 0
    false_negative = 0
    for result in results:
        expected = set(result.expected_agents)
        selected = set(result.selected_agents)
        true_positive += len(expected & selected)
        false_positive += len(selected - expected)
        false_negative += len(expected - selected)

    precision = _safe_div(true_positive, true_positive + false_positive)
    recall = _safe_div(true_positive, true_positive + false_negative)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    latencies = sorted(result.latency_ms for result in results)

    categories: dict[str, list[TaskResult]] = {}
    for result in results:
        categories.setdefault(result.category, []).append(result)

    return {
        "task_count": len(results),
        "success_rate": _rate(result.success for result in results),
        "route_accuracy": _rate(result.route_correct for result in results),
        "mode_accuracy": _rate(result.mode_correct for result in results),
        "agent_selection_precision": round(precision, 4),
        "agent_selection_recall": round(recall, 4),
        "agent_selection_f1": round(f1, 4),
        "avg_tool_calls": round(mean(result.tool_calls for result in results), 3),
        "avg_latency_ms": round(mean(latencies), 3),
        "p50_latency_ms": round(_percentile(latencies, 50), 3),
        "p95_latency_ms": round(_percentile(latencies, 95), 3),
        "category_breakdown": {
            category: {
                "task_count": len(items),
                "success_rate": _rate(item.success for item in items),
                "route_accuracy": _rate(item.route_correct for item in items),
                "mode_accuracy": _rate(item.mode_correct for item in items),
                "avg_latency_ms": round(mean(item.latency_ms for item in items), 3),
            }
            for category, items in sorted(categories.items())
        },
        "outcome_counts": dict(Counter(result.outcome or "route_only" for result in results)),
    }


def _rate(values: Any) -> float:
    items = list(values)
    if not items:
        return 0.0
    return round(sum(1 for item in items if item) / len(items), 4)


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _percentile(sorted_values: list[float], percentile: int) -> float:
    if not sorted_values:
        return 0.0
    index = max(0, ceil((percentile / 100) * len(sorted_values)) - 1)
    return sorted_values[min(index, len(sorted_values) - 1)]
