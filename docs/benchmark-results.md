# QuantOps AI Copilot Benchmark Results

These numbers were generated locally against the current repository state on 2026-08-21.

## Commands

```bash
python -m eval.run --dataset eval/tasks.json --mode router
python -m eval.run --dataset eval/tasks.json --mode orchestrator
cd backend
python -m pytest
python -m ruff check .
```

## Dataset

- Total tasks: 60
- Categories: document retrieval, multi-hop RAG, SQL querying, code generation, tool selection, multi-agent reasoning, failure recovery, finance workflows.
- Dataset file: `eval/tasks.json`

## Router Benchmark

- Success rate: 100.00%
- Route accuracy: 100.00%
- Mode accuracy: 100.00%
- Agent-selection precision: 100.00%
- Agent-selection recall: 100.00%
- Agent-selection F1: 100.00%
- Average latency: 0.022 ms
- p50 latency: 0.015 ms
- p95 latency: 0.061 ms
- Average tool calls: 0

Report files:

- `eval/runs/20260821T085903Z-router-report.json`
- `eval/runs/20260821T085903Z-router-summary.md`

## Orchestrator Benchmark

- Success rate: 0.00%
- Route accuracy: 100.00%
- Mode accuracy: 100.00%
- Agent-selection precision: 100.00%
- Agent-selection recall: 100.00%
- Agent-selection F1: 100.00%
- Average latency: 0.747 ms
- p50 latency: 0.638 ms
- p95 latency: 1.433 ms
- Average tool calls: 0

Report files:

- `eval/runs/20260821T085909Z-orchestrator-report.json`
- `eval/runs/20260821T085909Z-orchestrator-summary.md`

The end-to-end success rate is currently 0% because Phase 1 intentionally includes orchestration, routing, state, and evaluator contracts, but not the specialized Research, SQL, and Code agents. The benchmark is correctly surfacing the next implementation gap instead of hiding it.

## Resume-Safe Claims Today

- Built a reproducible 60-task benchmark suite for a QuantOps multi-agent AI copilot across retrieval, SQL, code, failure-recovery, and finance workflows.
- Implemented typed agent routing and orchestration contracts with trace IDs, execution plans, evaluator scoring, latency measurement, and saved JSON/Markdown evaluation reports.
- Improved deterministic router from 88.33% to 100.00% routing accuracy on the local benchmark by replacing substring keyword matching with token/phrase-aware routing.
- Added regression tests for benchmark-discovered routing failures such as `latest` matching `test`, plural document routing, and latency-log code tasks.
- Established an honest baseline showing 100.00% planning accuracy but 0.00% specialized-agent task completion before Phase 2 implementation.
