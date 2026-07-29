from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.operations import (
    OperationsSnapshot,
    WorkflowActionRequest,
    WorkflowActionResponse,
)
from app.services.operations_service import OperationsService

router = APIRouter()


@router.get("/snapshot", response_model=OperationsSnapshot)
async def snapshot(current_user: User = Depends(get_current_user)) -> OperationsSnapshot:
    _ = current_user
    return await OperationsService().snapshot()


@router.post("/actions", response_model=WorkflowActionResponse, status_code=202)
async def run_action(
    payload: WorkflowActionRequest,
    current_user: User = Depends(get_current_user),
) -> WorkflowActionResponse:
    return await OperationsService().run_action(
        user=current_user,
        action=payload.action,
        target=payload.target,
        reason=payload.reason,
    )


@router.get("/incidents/{incident_id}/prompt")
async def incident_prompt(
    incident_id: str,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    _ = current_user
    return {"question": OperationsService().incident_prompt(incident_id)}
