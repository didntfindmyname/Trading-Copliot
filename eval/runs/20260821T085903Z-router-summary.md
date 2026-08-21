# QuantOps Agent Evaluation Summary

- Created at: `2026-08-21T08:59:03.673335+00:00`
- Dataset: `eval\tasks.json`
- Mode: `router`
- Tasks: `60`
- Success rate: `100.00%`
- Route accuracy: `100.00%`
- Mode accuracy: `100.00%`
- Agent selection precision: `100.00%`
- Agent selection recall: `100.00%`
- Agent selection F1: `100.00%`
- Average latency: `0.022 ms`
- p50 latency: `0.015 ms`
- p95 latency: `0.061 ms`
- Average tool calls: `0`

## Category Breakdown

- `code_generation`: tasks=8, success=100.00%, route=100.00%, latency=0.021 ms
- `document_retrieval`: tasks=8, success=100.00%, route=100.00%, latency=0.062 ms
- `failure_recovery`: tasks=8, success=100.00%, route=100.00%, latency=0.015 ms
- `finance_workflows`: tasks=4, success=100.00%, route=100.00%, latency=0.015 ms
- `multi_agent_reasoning`: tasks=8, success=100.00%, route=100.00%, latency=0.015 ms
- `multi_hop_rag`: tasks=8, success=100.00%, route=100.00%, latency=0.014 ms
- `sql_querying`: tasks=8, success=100.00%, route=100.00%, latency=0.014 ms
- `tool_selection`: tasks=8, success=100.00%, route=100.00%, latency=0.015 ms

## Notes

- Token usage and inference cost are intentionally omitted in Phase 1.
- Tool-call metrics are expected to remain zero until MCP/tool-backed agents land.
