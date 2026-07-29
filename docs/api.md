# API Documentation

FastAPI serves interactive OpenAPI documentation at `/docs` and machine-readable OpenAPI JSON at `/openapi.json`.

Authentication uses JWT bearer tokens. Send `Authorization: Bearer <token>` for all endpoints except health and auth.

## Core Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Create a user |
| POST | `/api/v1/auth/login` | Exchange credentials for JWT |
| GET | `/api/v1/auth/me` | Return current user |
| POST | `/api/v1/documents` | Upload PDF, Markdown, TXT, or source file |
| GET | `/api/v1/documents` | Paginated document list |
| POST | `/api/v1/documents/{id}/index` | Synchronously index a document |
| GET | `/api/v1/search` | Semantic document search |
| POST | `/api/v1/ai/ask` | Ask the RAG copilot |
| GET | `/api/v1/chat/conversations` | Conversation history |
| GET | `/api/v1/usage/me` | Current user usage |
| GET | `/api/v1/admin/users` | Admin user list |
| GET | `/api/v1/admin/usage` | Admin usage rollup |

## Streaming

Set `stream=true` in `POST /api/v1/ai/ask` to receive Server-Sent Events. Each event contains a JSON token payload, followed by a terminal event with citations.

