# QuantOps Agent Evaluation Summary

- Created at: `2026-08-21T08:58:42.321152+00:00`
- Dataset: `eval\tasks.json`
- Mode: `router`
- Tasks: `60`
- Success rate: `93.33%`
- Route accuracy: `93.33%`
- Mode accuracy: `95.00%`
- Agent selection precision: `98.80%`
- Agent selection recall: `96.47%`
- Agent selection F1: `97.62%`
- Average latency: `0.029 ms`
- p50 latency: `0.015 ms`
- p95 latency: `0.072 ms`
- Average tool calls: `0`

## Category Breakdown

- `code_generation`: tasks=8, success=87.50%, route=87.50%, latency=0.015 ms
- `document_retrieval`: tasks=8, success=100.00%, route=100.00%, latency=0.076 ms
- `failure_recovery`: tasks=8, success=100.00%, route=100.00%, latency=0.015 ms
- `finance_workflows`: tasks=4, success=100.00%, route=100.00%, latency=0.014 ms
- `multi_agent_reasoning`: tasks=8, success=75.00%, route=75.00%, latency=0.014 ms
- `multi_hop_rag`: tasks=8, success=100.00%, route=100.00%, latency=0.062 ms
- `sql_querying`: tasks=8, success=100.00%, route=100.00%, latency=0.016 ms
- `tool_selection`: tasks=8, success=87.50%, route=87.50%, latency=0.014 ms

## Notes

- Token usage and inference cost are intentionally omitted in Phase 1.
- Tool-call metrics are expected to remain zero until MCP/tool-backed agents land.
