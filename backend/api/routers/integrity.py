from fastapi import APIRouter

from api.models.responses import BaseAPIResponse
from middleware.code_integrity import verify_system_integrity

router = APIRouter(prefix="/integrity", tags=["Integrity"])


@router.get("", response_model=BaseAPIResponse[dict])
@router.get("/status", response_model=BaseAPIResponse[dict])
def get_system_integrity():
    status_data = verify_system_integrity()
    return BaseAPIResponse(
        success=status_data["status"] == "PASSED", message="System Integrity Check Completed", data=status_data
    )
