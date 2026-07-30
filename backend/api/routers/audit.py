from fastapi import APIRouter

from api.models.requests import AuditSearchRequest
from api.models.responses import BaseAPIResponse
from api.services import audit_service

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("", response_model=BaseAPIResponse[list])
def get_recent_logs():
    return BaseAPIResponse(success=True, message="Success", data=audit_service.get_recent_logs())


@router.get("/export", response_model=BaseAPIResponse[str])
def export_logs():
    return BaseAPIResponse(success=True, message="Success", data=audit_service.export_logs())


@router.get("/{run_id}", response_model=BaseAPIResponse[list])
def get_logs_for_run(run_id: str):
    return BaseAPIResponse(success=True, message="Success", data=audit_service.get_logs_for_run(run_id))


@router.post("/search", response_model=BaseAPIResponse[list])
def search_logs(request: AuditSearchRequest):
    return BaseAPIResponse(
        success=True,
        message="Success",
        data=audit_service.search_logs(
            event_type=request.event_type, agent_id=request.agent_id, decision=request.decision, limit=request.limit
        ),
    )
