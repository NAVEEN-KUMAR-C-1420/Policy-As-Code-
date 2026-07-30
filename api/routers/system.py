from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.services import system_service

router = APIRouter(tags=["System"])

@router.get("/health", response_model=BaseAPIResponse[dict])
def get_health():
    return BaseAPIResponse(success=True, message="Success", data=system_service.get_health())

@router.get("/system/status", response_model=BaseAPIResponse[dict])
def get_system_status():
    return BaseAPIResponse(success=True, message="Success", data=system_service.get_system_status())

@router.get("/system/version", response_model=BaseAPIResponse[dict])
def get_system_version():
    return BaseAPIResponse(success=True, message="Success", data=system_service.get_system_version())

@router.get("/metrics", response_model=BaseAPIResponse[dict])
def get_metrics():
    return BaseAPIResponse(success=True, message="Success", data=system_service.get_metrics())
