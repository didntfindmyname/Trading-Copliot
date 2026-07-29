from __future__ import annotations

import hashlib
import random
from datetime import UTC, datetime, timedelta

from app.models.user import User
from app.schemas.operations import (
    FeedStatus,
    Incident,
    OperationsSnapshot,
    WorkerStatus,
    WorkflowActionResponse,
)


class OperationsService:
    venues = ("NSE-CASH", "NSE-FO", "BSE-CASH", "MCX")

    async def snapshot(self) -> OperationsSnapshot:
        now = datetime.now(UTC)
        rng = random.Random(now.strftime("%Y-%m-%d-%H-%M"))
        feeds = [
            FeedStatus(
                venue=venue,
                asset_class="equities" if "CASH" in venue else "derivatives",
                status=self._feed_status(index, rng),
                latency_ms=rng.randint(2, 38) + (65 if index == 1 else 0),
                dropped_messages=rng.randint(0, 4) + (12 if index == 1 else 0),
                stale_symbols=rng.randint(0, 2) + (8 if index == 1 else 0),
                heartbeat_age_seconds=rng.randint(1, 8) + (24 if index == 1 else 0),
            )
            for index, venue in enumerate(self.venues)
        ]
        workers = [
            WorkerStatus(
                name="md-ingestion-a",
                queue="market-data",
                status="degraded",
                queue_depth=rng.randint(350, 900),
                failed_jobs=rng.randint(2, 7),
                processed_per_minute=rng.randint(4200, 5200),
            ),
            WorkerStatus(
                name="feature-writer-1",
                queue="features",
                status="healthy",
                queue_depth=rng.randint(10, 80),
                failed_jobs=0,
                processed_per_minute=rng.randint(1600, 2400),
            ),
            WorkerStatus(
                name="risk-limit-sync",
                queue="ops",
                status="healthy",
                queue_depth=rng.randint(0, 15),
                failed_jobs=0,
                processed_per_minute=rng.randint(80, 160),
            ),
        ]
        incidents = [
            Incident(
                id="INC-MD-1042",
                severity="high",
                title="NSE-FO heartbeat age above threshold",
                service="market-data",
                status="open",
                detected_at=now - timedelta(minutes=7),
                suggested_action=(
                    "Check exchange gateway heartbeat, inspect Redis queue depth, "
                    "then restart md-ingestion-a if upstream is healthy."
                ),
            )
        ]
        overall_status = (
            "degraded" if any(feed.status != "healthy" for feed in feeds) else "healthy"
        )
        return OperationsSnapshot(
            generated_at=now,
            market_open=self._is_market_open(now),
            overall_status=overall_status,
            feeds=feeds,
            workers=workers,
            incidents=incidents,
        )

    async def run_action(
        self,
        *,
        user: User,
        action: str,
        target: str,
        reason: str,
    ) -> WorkflowActionResponse:
        now = datetime.now(UTC)
        digest = hashlib.sha256(
            f"{action}:{target}:{reason}:{now.isoformat()}".encode()
        ).hexdigest()
        action_id = f"ACT-{digest[:8].upper()}"
        messages = {
            "restart_worker": f"Restart queued for worker {target}.",
            "replay_gap": f"Replay requested for sequence gap on {target}.",
            "ack_incident": f"Incident {target} acknowledged.",
            "run_health_check": f"Health check triggered for {target}.",
        }
        return WorkflowActionResponse(
            action_id=action_id,
            status="accepted",
            message=messages[action],
            audit_note=f"{user.email} requested {action} because: {reason}",
            created_at=now,
        )

    def incident_prompt(self, incident_id: str) -> str:
        return (
            f"Investigate {incident_id}. Use the market data runbook and explain the recovery "
            "steps, safety checks, and escalation criteria for a quant trading operations team."
        )

    def _feed_status(self, index: int, rng: random.Random) -> str:
        if index == 1:
            return "degraded"
        return "healthy" if rng.random() > 0.08 else "watch"

    def _is_market_open(self, now: datetime) -> bool:
        return 3 <= now.hour < 10
