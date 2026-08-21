# QuantOps AI Copilot Multi-Agent Roadmap

## A. Current Architecture

The existing project is a FastAPI backend with a React/Vite frontend and Dockerized support services. The backend exposes versioned REST APIs under `/api/v1`, uses SQLAlchemy async sessions for relational state, Redis for caching/rate-limit-adjacent runtime services, Qdrant for vector search, and Prometheus metrics at `/metrics`.

The current AI path is a conventional RAG workflow:

1. `/api/v1/ai/ask` receives an authenticated question.
2. `RagService` loads conversation memory from PostgreSQL.
3. `EmbeddingService` embeds the query.
4. `VectorStore` searches Qdrant.
5. `LLMService` renders a grounded prompt and returns an answer.
6. `ConversationRepository` persists user/assistant turns, citations, token counts, and an evaluation score.
7. Prometheus counters track token usage, cache events, and latest evaluation score.

The operations APIs provide QuantOps-flavored workflow data such as market-data feed health, worker status, incidents, and operator actions.

## B. Reusable Components

Keep these components and extend them incrementally:

- `RagService`, `EmbeddingService`, and `VectorStore` for Research Agent retrieval.
- `ConversationRepository` and conversation models for durable chat memory.
- `DocumentRepository`, chunking, extraction, and indexing tasks for ingestion.
- Existing auth, rate limiting, request context middleware, structured logging, and metrics.
- Operations service as the seed for incident-analysis and system-metrics tools.
- Docker Compose, CI, Prometheus, and Grafana scaffolding.

## C. Missing Components

The repository did not yet include:

- Typed agent execution state separate from durable conversation memory.
- Orchestrator routing and agent execution control.
- Specialized Research, SQL, Code, and Evaluator agents.
- MCP tool server and tool schemas.
- Tool invocation audit records with latency, success/failure, and metadata.
- Read-only SQL validation/execution layer for analytical questions.
- Python execution sandbox.
- Automated agent evaluation dataset and benchmark runner.
- Trace-oriented observability for full agent executions.
- Prompt/model/evaluation versioning.
- Agent security tests and failure-recovery tests.

## D. Implementation Phases

### Phase 1 - Agent Foundation

Add typed LLM provider interfaces, structured agent state, deterministic first-pass routing, an orchestrator, an evaluator, and a protected `/api/v1/agents/run` endpoint. This phase establishes execution contracts and honest partial/failure reporting.

### Phase 2 - Specialized Agents

Implement Research, SQL, and Code agents behind the orchestrator. Reuse `RagService` for retrieval, add read-only SQL safety, and add a restricted Python execution tool.

### Phase 3 - MCP

Expose project tools through MCP with schemas, validation, timeouts, structured outputs, and logs. Route agent tool use through the MCP client boundary wherever practical.

### Phase 4 - Evaluation

Add `eval/tasks.json`, an async benchmark runner, task-level graders, stored run outputs, and summary reports for success rate, tool-selection accuracy, hallucination rate, latency, token usage, and estimated cost.

### Phase 5 - Observability and MLOps

Add request trace views, model/prompt version metadata, agent/tool latency metrics, error-rate monitoring, `/ready`, and deployment-focused configuration separation.

### Phase 6 - Production Hardening

Expand security controls, failure recovery, circuit breakers, CI coverage, README architecture diagrams, and safe agentic coding workflows.

## Phase 1 Status

Implemented:

- LLM provider abstraction with local and OpenAI-compatible providers.
- Agent state models for execution plan, intermediate outputs, citations, tool results, errors, retries, and final outcome.
- Request router supporting sequential or parallel agent plans.
- Orchestrator that executes registered agents, handles timeouts, records state, and does not claim unavailable agents ran.
- Evaluator/Critic that scores completed agent outputs and reports findings.
- Authenticated `/api/v1/agents/run` endpoint exposing trace ID, route, plan, result details, evaluation, citations, and tool calls.

Not implemented in Phase 1:

- Specialized Research/SQL/Code execution.
- MCP server/tool bridge.
- Real tool calls.
- Benchmark dataset and runner.
