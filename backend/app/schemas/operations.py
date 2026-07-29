from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FeedStatus(BaseModel):
    venue: str
    asset_class: str
    status: str
    latency_ms: int
    dropped_messages: int
    stale_symbols: int
    heartbeat_age_seconds: int


class WorkerStatus(BaseModel):
    name: str
    queue: str
    status: str
    queue_depth: int
    failed_jobs: int
    processed_per_minute: int
    last_restart_at: datetime | None = None


class Incident(BaseModel):
    id: str
    severity: str
    title: str
    service: str
    status: str
    detected_at: datetime
    suggested_action: str


class OperationsSnapshot(BaseModel):
    generated_at: datetime
    market_open: bool
    overall_status: str
    feeds: list[FeedStatus]
    workers: list[WorkerStatus]
    incidents: list[Incident]


class WorkflowActionRequest(BaseModel):
    action: str = Field(pattern="^(restart_worker|replay_gap|ack_incident|run_health_check)$")
    target: str = Field(min_length=2, max_length=120)
    reason: str = Field(min_length=3, max_length=500)


class WorkflowActionResponse(BaseModel):
    action_id: str
    status: str
    message: str
    audit_note: str
    created_at: datetime
