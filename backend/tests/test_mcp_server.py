from __future__ import annotations

from app.mcp.server import mcp


async def test_mcp_server_registers_quantops_tools() -> None:
    tools = await mcp.list_tools()
    tool_names = {tool.name for tool in tools}

    assert {
        "search_documents",
        "retrieve_document",
        "get_database_schema",
        "run_sql_query",
        "search_conversation_memory",
        "get_system_metrics",
        "execute_python",
    } <= tool_names
