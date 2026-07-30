from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from common.repositories import HITLRepository

router = APIRouter(prefix="/hitl", tags=["HITL"])

@router.post("/approve/{request_id}", response_model=BaseAPIResponse[dict])
def approve_hitl(request_id: int):
    HITLRepository.update_status(request_id, "APPROVED")
    return BaseAPIResponse(success=True, message="HITL request approved", data={})

@router.post("/reject/{request_id}", response_model=BaseAPIResponse[dict])
def reject_hitl(request_id: int):
    HITLRepository.update_status(request_id, "REJECTED")
    return BaseAPIResponse(success=True, message="HITL request rejected", data={})
