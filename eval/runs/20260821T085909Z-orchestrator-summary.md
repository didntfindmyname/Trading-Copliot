# QuantOps Agent Evaluation Summary

- Created at: `2026-08-21T08:59:09.349659+00:00`
- Dataset: `eval\tasks.json`
- Mode: `orchestrator`
- Tasks: `60`
- Success rate: `0.00%`
- Route accuracy: `100.00%`
- Mode accuracy: `100.00%`
- Agent selection precision: `100.00%`
- Agent selection recall: `100.00%`
- Agent selection F1: `100.00%`
- Average latency: `0.747 ms`
- p50 latency: `0.638 ms`
- p95 latency: `1.433 ms`
- Average tool calls: `0`

## Category Breakdown

- `code_generation`: tasks=8, success=0.00%, route=100.00%, latency=0.639 ms
- `document_retrieval`: tasks=8, success=0.00%, route=100.00%, latency=1.141 ms
- `failure_recovery`: tasks=8, success=0.00%, route=100.00%, latency=0.339 ms
- `finance_workflows`: tasks=4, success=0.00%, route=100.00%, latency=0.953 ms
- `multi_agent_reasoning`: tasks=8, success=0.00%, route=100.00%, latency=0.563 ms
- `multi_hop_rag`: tasks=8, success=0.00%, route=100.00%, latency=0.912 ms
- `sql_querying`: tasks=8, success=0.00%, route=100.00%, latency=0.820 ms
- `tool_selection`: tasks=8, success=0.00%, route=100.00%, latency=0.713 ms

## Notes

- Token usage and inference cost are intentionally omitted in Phase 1.
- Tool-call metrics are expected to remain zero until MCP/tool-backed agents land.
