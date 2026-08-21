from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    agents,
    ai,
    auth,
    chat,
    documents,
    health,
    operations,
    search,
    usage,
)

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(usage.router, prefix="/usage", tags=["usage"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(operations.router, prefix="/operations", tags=["operations"])
