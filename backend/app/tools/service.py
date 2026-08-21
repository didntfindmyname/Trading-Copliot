from __future__ import annotations

import asyncio
import sys
from typing import Any, cast

import sqlparse
from sqlalchemy import inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message
from app.repositories.document_repository import DocumentRepository
from app.services.operations_service import OperationsService
from app.services.rag_service import RagService
from app.tools.base import Tool
from app.tools.schemas import (
    ConversationMemoryHit,
    DatabaseColumnSchema,
    DatabaseTableSchema,
    DocumentChunkRead,
    ExecutePythonInput,
    ExecutePythonOutput,
    GetDatabaseSchemaInput,
    GetDatabaseSchemaOutput,
    GetSystemMetricsInput,
    GetSystemMetricsOutput,
    RetrieveDocumentInput,
    RetrieveDocumentOutput,
    RunSqlQueryInput,
    RunSqlQueryOutput,
    SearchConversationMemoryInput,
    SearchConversationMemoryOutput,
    SearchDocumentsInput,
    SearchDocumentsOutput,
    ToolExecutionEnvelope,
)


class ToolSafetyError(ValueError):
    pass


class SearchDocumentsTool(Tool[SearchDocumentsInput, SearchDocumentsOutput]):
    name = "search_documents"
    description = "Search indexed QuantOps documents through semantic retrieval."
    input_model = SearchDocumentsInput

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, payload: SearchDocumentsInput) -> SearchDocumentsOutput:
        results = await RagService(self.session).search(payload.query, payload.top_k)
        return SearchDocumentsOutput(query=payload.query, results=results)


class RetrieveDocumentTool(Tool[RetrieveDocumentInput, RetrieveDocumentOutput]):
    name = "retrieve_document"
    description = "Retrieve a specific document and optionally its indexed chunks."
    input_model = RetrieveDocumentInput

    def __init__(self, session: AsyncSession) -> None:
        self.documents = DocumentRepository(session)

    async def execute(self, payload: RetrieveDocumentInput) -> RetrieveDocumentOutput:
        document = await self.documents.get_with_chunks(payload.document_id)
        if document is None:
            raise LookupError("Document not found")

        content = document.content[: payload.max_content_chars]
        chunks = []
        if payload.include_chunks:
            chunks = [
                DocumentChunkRead(
                    id=chunk.id,
                    ordinal=chunk.ordinal,
                    content=chunk.content[: payload.max_content_chars],
                    token_count=chunk.token_count,
                )
                for chunk in sorted(document.chunks, key=lambda item: item.ordinal)
            ]
        return RetrieveDocumentOutput(
            document_id=document.id,
            title=document.title,
            filename=document.filename,
            status=document.status,
            content=content,
            truncated=len(document.content) > len(content),
            chunks=chunks,
        )


class GetDatabaseSchemaTool(Tool[GetDatabaseSchemaInput, GetDatabaseSchemaOutput]):
    name = "get_database_schema"
    description = "Inspect application database tables and columns without exposing secrets."
    input_model = GetDatabaseSchemaInput

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, payload: GetDatabaseSchemaInput) -> GetDatabaseSchemaOutput:
        requested = set(payload.table_names or [])
        connection = await self.session.connection()

        def load_schema(sync_connection: Any) -> list[DatabaseTableSchema]:
            inspector = inspect(sync_connection)
            table_names = [
                name for name in inspector.get_table_names() if not requested or name in requested
            ]
            return [
                DatabaseTableSchema(
                    name=table_name,
                    columns=[
                        DatabaseColumnSchema(
                            name=str(column["name"]),
                            type=str(column["type"]),
                            nullable=bool(column.get("nullable", True)),
                        )
                        for column in inspector.get_columns(table_name)
                    ],
                )
                for table_name in table_names
            ]

        tables = await connection.run_sync(load_schema)
        return GetDatabaseSchemaOutput(tables=tables)


class RunSqlQueryTool(Tool[RunSqlQueryInput, RunSqlQueryOutput]):
    name = "run_sql_query"
    description = "Execute one validated read-only SQL SELECT query with a row limit."
    input_model = RunSqlQueryInput
    forbidden_statement_types = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"}

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, payload: RunSqlQueryInput) -> RunSqlQueryOutput:
        sql = self._validate_read_only_sql(payload.sql)
        limited_sql = f"SELECT * FROM ({sql}) AS quantops_readonly_query LIMIT :row_limit"
        result = await asyncio.wait_for(
            self.session.execute(text(limited_sql), {"row_limit": payload.row_limit + 1}),
            timeout=payload.timeout_seconds,
        )
        rows = result.mappings().all()
        truncated = len(rows) > payload.row_limit
        visible_rows = rows[: payload.row_limit]
        return RunSqlQueryOutput(
            columns=list(result.keys()),
            rows=[dict(row) for row in visible_rows],
            row_count=len(visible_rows),
            truncated=truncated,
        )

    def _validate_read_only_sql(self, sql: str) -> str:
        statements = [statement for statement in sqlparse.split(sql) if statement.strip()]
        if len(statements) != 1:
            raise ToolSafetyError("Only one SQL statement is allowed.")
        statement = cast(Any, sqlparse.parse(statements[0])[0])
        statement_type = str(statement.get_type()).upper()
        if statement_type != "SELECT":
            raise ToolSafetyError("Only read-only SELECT queries are allowed.")
        for token in list(statement.flatten()):
            token_value = token.value.upper()
            if token_value in self.forbidden_statement_types:
                raise ToolSafetyError(f"Forbidden SQL operation: {token_value}")
        return statements[0].strip().rstrip(";")


class SearchConversationMemoryTool(
    Tool[SearchConversationMemoryInput, SearchConversationMemoryOutput]
):
    name = "search_conversation_memory"
    description = "Search prior conversation messages separately from retrieved documents."
    input_model = SearchConversationMemoryInput

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self, payload: SearchConversationMemoryInput
    ) -> SearchConversationMemoryOutput:
        pattern = f"%{payload.query}%"
        statement = (
            select(Message, Conversation)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Message.content.ilike(pattern))
            .order_by(Message.created_at.desc())
            .limit(payload.limit)
        )
        if payload.user_id:
            statement = statement.where(Conversation.user_id == payload.user_id)
        result = await self.session.execute(statement)
        hits = [
            ConversationMemoryHit(
                conversation_id=conversation.id,
                message_id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message, conversation in result.all()
        ]
        return SearchConversationMemoryOutput(query=payload.query, results=hits)


class GetSystemMetricsTool(Tool[GetSystemMetricsInput, GetSystemMetricsOutput]):
    name = "get_system_metrics"
    description = "Return QuantOps operations metrics useful for incident analysis."
    input_model = GetSystemMetricsInput

    async def execute(self, payload: GetSystemMetricsInput) -> GetSystemMetricsOutput:
        _ = payload
        return GetSystemMetricsOutput(snapshot=await OperationsService().snapshot())


class ExecutePythonTool(Tool[ExecutePythonInput, ExecutePythonOutput]):
    name = "execute_python"
    description = (
        "Run small Python snippets in an isolated subprocess with time and output limits. "
        "This is not a hardened security sandbox."
    )
    input_model = ExecutePythonInput

    async def execute(self, payload: ExecutePythonInput) -> ExecutePythonOutput:
        wrapper = self._wrap_code(payload.code)
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-I",
            "-c",
            wrapper,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=payload.timeout_seconds,
            )
            timed_out = False
        except TimeoutError:
            process.kill()
            stdout_bytes, stderr_bytes = await process.communicate()
            timed_out = True

        stdout = stdout_bytes.decode(errors="replace")[: payload.max_output_chars]
        stderr = stderr_bytes.decode(errors="replace")[: payload.max_output_chars]
        return ExecutePythonOutput(
            stdout=stdout,
            stderr=stderr,
            return_code=int(process.returncode or 0),
            timed_out=timed_out,
            safety_level="restricted-subprocess",
        )

    def _wrap_code(self, code: str) -> str:
        return (
            "import math, statistics\n"
            "allowed_builtins = {\n"
            "    'abs': abs, 'all': all, 'any': any, 'bool': bool, 'dict': dict,\n"
            "    'enumerate': enumerate, 'float': float, 'int': int, 'len': len,\n"
            "    'list': list, 'max': max, 'min': min, 'pow': pow, 'print': print,\n"
            "    'range': range, 'round': round, 'set': set, 'sorted': sorted,\n"
            "    'str': str, 'sum': sum, 'tuple': tuple, 'zip': zip,\n"
            "}\n"
            "globals_dict = {'__builtins__': allowed_builtins, 'math': math, "
            "'statistics': statistics}\n"
            f"exec({code!r}, globals_dict, globals_dict)\n"
        )


class QuantOpsToolService:
    def __init__(self, session: AsyncSession) -> None:
        self.tools: dict[str, Tool[Any, Any]] = {
            "search_documents": SearchDocumentsTool(session),
            "retrieve_document": RetrieveDocumentTool(session),
            "get_database_schema": GetDatabaseSchemaTool(session),
            "run_sql_query": RunSqlQueryTool(session),
            "search_conversation_memory": SearchConversationMemoryTool(session),
            "get_system_metrics": GetSystemMetricsTool(),
            "execute_python": ExecutePythonTool(),
        }

    async def execute(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        agent_name: str = "mcp",
    ) -> ToolExecutionEnvelope:
        tool = self.tools.get(tool_name)
        if tool is None:
            raise LookupError(f"Unknown tool: {tool_name}")
        return await tool.run(payload=arguments, agent_name=agent_name)
