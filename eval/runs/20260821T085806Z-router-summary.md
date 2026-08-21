# QuantOps Agent Evaluation Summary

- Created at: `2026-08-21T08:58:06.250126+00:00`
- Dataset: `eval\tasks.json`
- Mode: `router`
- Tasks: `60`
- Success rate: `88.33%`
- Route accuracy: `88.33%`
- Mode accuracy: `90.00%`
- Agent selection precision: `91.40%`
- Agent selection recall: `100.00%`
- Agent selection F1: `95.51%`
- Average latency: `0.017 ms`
- p50 latency: `0.009 ms`
- p95 latency: `0.049 ms`
- Average tool calls: `0`

## Category Breakdown

- `code_generation`: tasks=8, success=62.50%, route=62.50%, latency=0.010 ms
- `document_retrieval`: tasks=8, success=100.00%, route=100.00%, latency=0.021 ms
- `failure_recovery`: tasks=8, success=87.50%, route=87.50%, latency=0.034 ms
- `finance_workflows`: tasks=4, success=75.00%, route=75.00%, latency=0.015 ms
- `multi_agent_reasoning`: tasks=8, success=100.00%, route=100.00%, latency=0.009 ms
- `multi_hop_rag`: tasks=8, success=87.50%, route=87.50%, latency=0.010 ms
- `sql_querying`: tasks=8, success=87.50%, route=87.50%, latency=0.009 ms
- `tool_selection`: tasks=8, success=100.00%, route=100.00%, latency=0.026 ms

## Notes

- Token usage and inference cost are intentionally omitted in Phase 1.
- Tool-call metrics are expected to remain zero until MCP/tool-backed agents land.
