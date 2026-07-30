from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", response_model=BaseAPIResponse[list])
def list_reports():
    return BaseAPIResponse(success=True, message="Success", data=report_service.list_reports())

@router.get("/{report_id}", response_model=BaseAPIResponse[dict])
def get_report(report_id: int):
    return BaseAPIResponse(success=True, message="Success", data=report_service.get_report(report_id))

@router.get("/download/{report_id}", response_model=BaseAPIResponse[str])
def download_report(report_id: int):
    return BaseAPIResponse(success=True, message="Success", data=report_service.download_report(report_id))

@router.delete("/{report_id}", response_model=BaseAPIResponse[dict])
def delete_report(report_id: int):
    return BaseAPIResponse(success=True, message="Success", data=report_service.delete_report(report_id))
