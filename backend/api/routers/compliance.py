from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.services import compliance_service

router = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.get("/report", response_model=BaseAPIResponse[dict])
def get_compliance_report():
    return BaseAPIResponse(success=True, message="Success", data=compliance_service.get_compliance_report())

@router.get("/summary", response_model=BaseAPIResponse[dict])
def get_compliance_summary():
    return BaseAPIResponse(success=True, message="Success", data=compliance_service.get_compliance_summary())

@router.post("/check", response_model=BaseAPIResponse[dict])
def run_compliance_checks():
    return BaseAPIResponse(success=True, message="Success", data=compliance_service.run_compliance_checks())
