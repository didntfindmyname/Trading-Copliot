from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Athena AI Engineering Copilot"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(default="local-dev-secret-change-me", min_length=16)
    access_token_expire_minutes: int = 60

    database_url: str = "sqlite+aiosqlite:///./athena.db"
    sync_database_url: str = "sqlite:///./athena.db"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    qdrant_url: AnyHttpUrl | str = "http://localhost:6333"
    qdrant_collection: str = "athena_chunks"

    llm_provider: Literal["local", "openai"] = "local"
    embedding_provider: Literal["local", "openai"] = "local"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    local_embedding_dimensions: int = 384

    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    rate_limit_per_minute: int = 120
    max_upload_mb: int = 20
    log_level: str = "INFO"
    max_tool_calls: int = 8
    max_agent_iterations: int = 6
    agent_request_timeout_seconds: float = 45.0

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
