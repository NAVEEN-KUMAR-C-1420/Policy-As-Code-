from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.services import drift_service

router = APIRouter(prefix="/drift", tags=["Drift Detection"])

@router.get("", response_model=BaseAPIResponse[dict])
def get_drift_report():
    return BaseAPIResponse(success=True, message="Success", data=drift_service.get_drift_report())

@router.get("/{agent_id}", response_model=BaseAPIResponse[dict])
def get_agent_drift(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=drift_service.get_agent_drift(agent_id))

@router.post("/check", response_model=BaseAPIResponse[dict])
def check_drift():
    return BaseAPIResponse(success=True, message="Success", data=drift_service.check_drift())
