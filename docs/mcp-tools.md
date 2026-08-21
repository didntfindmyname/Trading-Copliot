# QuantOps MCP Tool Server

The project now exposes a real MCP stdio server backed by the official Python MCP SDK `mcp>=1.9.1,<2.0`.

Run it from the backend package:

```bash
cd backend
python -m app.mcp
```

The MCP transport is intentionally thin. Business logic lives in `app.tools`, so internal agents and external MCP clients can call the same typed tool layer.

## Exposed Tools

- `search_documents`: semantic document search through the existing RAG stack.
- `retrieve_document`: retrieve one document and optionally its chunks.
- `get_database_schema`: inspect database tables and columns.
- `run_sql_query`: execute one validated read-only `SELECT` query with a row limit.
- `search_conversation_memory`: search prior conversation messages separately from RAG documents.
- `get_system_metrics`: return QuantOps operations metrics for incident workflows.
- `execute_python`: run small Python snippets in an isolated subprocess with timeout and output limits.

Every tool response includes:

- `tool_name`
- `agent_name`
- `arguments`
- `start_time`
- `end_time`
- `latency_ms`
- `success`
- `error_type`
- `trace_id`

## Safety Boundaries

- SQL execution accepts one statement only and requires a parsed `SELECT` statement.
- SQL mutation statements such as `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, and `TRUNCATE` are rejected before execution.
- SQL results are wrapped with a configurable row limit.
- Python execution uses `sys.executable -I` in a subprocess with restricted builtins, timeout, and output limits.
- Python execution is not a hardened security sandbox and should not be exposed to untrusted public users without stronger isolation such as containers or a remote sandbox service.

## Current Limitations

- The MCP server currently supports stdio transport.
- Specialized Research, SQL, and Code agents do not yet call this tool layer directly.
- End-to-end benchmark completion metrics have not been rerun against real tool-backed agents because those agents are still pending.
