from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.metrics import CACHE_EVENTS


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, redis_client: Redis | None = None) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.redis = redis_client or Redis.from_url(settings.redis_url, decode_responses=True)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path in {"/health", "/ready", "/metrics"}:
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        minute = int(time.time() // 60)
        key = f"rate:{client}:{minute}"
        try:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, 90)
            if count > settings.rate_limit_per_minute:
                CACHE_EVENTS.labels("rate_limited").inc()
                return Response(
                    "Rate limit exceeded", status_code=status.HTTP_429_TOO_MANY_REQUESTS
                )
        except Exception:
            CACHE_EVENTS.labels("rate_limit_bypass").inc()
        return await call_next(request)
