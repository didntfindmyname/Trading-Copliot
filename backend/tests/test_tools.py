from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.tools.service import QuantOpsToolService


async def test_database_schema_tool_returns_tables(session: AsyncSession) -> None:
    service = QuantOpsToolService(session)

    envelope = await service.execute(
        tool_name="get_database_schema",
        arguments={"table_names": ["users"], "trace_id": "trace-schema"},
        agent_name="sql",
    )

    assert envelope.metadata.success is True
    assert envelope.metadata.tool_name == "get_database_schema"
    assert envelope.metadata.agent_name == "sql"
    assert envelope.metadata.trace_id == "trace-schema"
    assert envelope.result is not None
    assert envelope.result["tables"][0]["name"] == "users"


async def test_sql_tool_rejects_mutating_statement(session: AsyncSession) -> None:
    service = QuantOpsToolService(session)

    envelope = await service.execute(
        tool_name="run_sql_query",
        arguments={"sql": "DELETE FROM users", "trace_id": "trace-sql"},
        agent_name="sql",
    )

    assert envelope.metadata.success is False
    assert envelope.metadata.error_type == "ToolSafetyError"
    assert envelope.error is not None
    assert "SELECT" in envelope.error


async def test_sql_tool_executes_read_only_query(session: AsyncSession) -> None:
    user = User(
        email="mcp@athena.local",
        full_name="MCP Tester",
        hashed_password="hashed",
        role="developer",
    )
    session.add(user)
    await session.commit()
    service = QuantOpsToolService(session)

    envelope = await service.execute(
        tool_name="run_sql_query",
        arguments={
            "sql": "SELECT email, role FROM users ORDER BY email",
            "row_limit": 5,
        },
        agent_name="sql",
    )

    assert envelope.metadata.success is True
    assert envelope.result is not None
    assert envelope.result["row_count"] == 1
    assert envelope.result["rows"][0]["email"] == "mcp@athena.local"


async def test_conversation_memory_tool_searches_messages(session: AsyncSession) -> None:
    user = User(
        email="memory@athena.local",
        full_name="Memory Tester",
        hashed_password="hashed",
        role="developer",
    )
    session.add(user)
    await session.flush()
    conversation = Conversation(user_id=user.id, title="Incident")
    session.add(conversation)
    await session.flush()
    session.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content="NSE-FO heartbeat recovery requires checking queue depth.",
        )
    )
    await session.commit()
    service = QuantOpsToolService(session)

    envelope = await service.execute(
        tool_name="search_conversation_memory",
        arguments={"query": "heartbeat", "user_id": user.id},
        agent_name="research",
    )

    assert envelope.metadata.success is True
    assert envelope.result is not None
    assert envelope.result["results"][0]["conversation_id"] == conversation.id


async def test_execute_python_tool_runs_with_output_limit(session: AsyncSession) -> None:
    service = QuantOpsToolService(session)

    envelope = await service.execute(
        tool_name="execute_python",
        arguments={"code": "print(sum([1, 2, 3]))"},
        agent_name="code",
    )

    assert envelope.metadata.success is True
    assert envelope.result is not None
    assert envelope.result["stdout"].strip() == "6"
    assert envelope.result["safety_level"] == "restricted-subprocess"
