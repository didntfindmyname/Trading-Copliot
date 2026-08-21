from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from app.db.session import AsyncSessionLocal
from app.tools.service import QuantOpsToolService

mcp = FastMCP(
    "QuantOps AI Copilot",
    instructions=(
        "Expose QuantOps document search, database inspection, read-only SQL, "
        "conversation memory, metrics, and restricted Python tools. All tool "
        "responses include structured execution metadata."
    ),
)


async def _execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, object]:
    async with AsyncSessionLocal() as session:
        service = QuantOpsToolService(session)
        envelope = await service.execute(
            tool_name=tool_name,
            arguments=arguments,
            agent_name="mcp",
        )
        return envelope.model_dump(mode="json")


@mcp.tool()
async def search_documents(
    query: str,
    top_k: int = 5,
    trace_id: str | None = None,
) -> dict[str, object]:
    """Search indexed QuantOps documents and return citation-ready chunks."""
    return await _execute_tool(
        "search_documents",
        {"query": query, "top_k": top_k, "trace_id": trace_id},
    )


@mcp.tool()
async def retrieve_document(
    document_id: str,
    include_chunks: bool = True,
    max_content_chars: int = 4000,
    trace_id: str | None = None,
) -> dict[str, object]:
    """Retrieve a specific document and optionally its chunks."""
    return await _execute_tool(
        "retrieve_document",
        {
            "document_id": document_id,
            "include_chunks": include_chunks,
            "max_content_chars": max_content_chars,
            "trace_id": trace_id,
        },
    )


@mcp.tool()
async def get_database_schema(
    table_names: list[str] | None = None,
    trace_id: str | None = None,
) -> dict[str, object]:
    """Inspect allowed database tables and columns."""
    return await _execute_tool(
        "get_database_schema",
        {"table_names": table_names, "trace_id": trace_id},
    )


@mcp.tool()
async def run_sql_query(
    sql: str,
    row_limit: int = 100,
    timeout_seconds: float = 5.0,
    trace_id: str | None = None,
) -> dict[str, object]:
    """Execute one validated read-only SQL SELECT query with a row limit."""
    return await _execute_tool(
        "run_sql_query",
        {
            "sql": sql,
            "row_limit": row_limit,
            "timeout_seconds": timeout_seconds,
            "trace_id": trace_id,
        },
    )


@mcp.tool()
async def search_conversation_memory(
    query: str,
    user_id: str | None = None,
    limit: int = 5,
    trace_id: str | None = None,
) -> dict[str, object]:
    """Search prior conversation messages separately from RAG documents."""
    return await _execute_tool(
        "search_conversation_memory",
        {"query": query, "user_id": user_id, "limit": limit, "trace_id": trace_id},
    )


@mcp.tool()
async def get_system_metrics(trace_id: str | None = None) -> dict[str, object]:
    """Return QuantOps operations metrics for incident analysis workflows."""
    return await _execute_tool("get_system_metrics", {"trace_id": trace_id})


@mcp.tool()
async def execute_python(
    code: str,
    timeout_seconds: float = 2.0,
    max_output_chars: int = 4000,
    trace_id: str | None = None,
) -> dict[str, object]:
    """Run a small Python snippet in an isolated subprocess with strict limits."""
    return await _execute_tool(
        "execute_python",
        {
            "code": code,
            "timeout_seconds": timeout_seconds,
            "max_output_chars": max_output_chars,
            "trace_id": trace_id,
        },
    )


def main() -> None:
    mcp.run()
