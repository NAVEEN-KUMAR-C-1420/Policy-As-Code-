from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.services import version_service

router = APIRouter(prefix="/versions", tags=["Global Versions"])

@router.get("", response_model=BaseAPIResponse[list])
@router.get("/history", response_model=BaseAPIResponse[list])
def list_global_versions():
    return BaseAPIResponse(success=True, message="Success", data=version_service.get_all_global_versions())

@router.get("/current", response_model=BaseAPIResponse[dict])
def get_current_global_version():
    data = version_service.get_global_active_version()
    return BaseAPIResponse(success=True if data else False, message="Success" if data else "No active version", data=data)

@router.get("/{version_number}", response_model=BaseAPIResponse[dict])
def get_global_version(version_number: int):
    data = version_service.get_global_version(version_number)
    return BaseAPIResponse(success=True if data else False, message="Success" if data else "Version not found", data=data)

@router.get("/git/{commit_sha}", response_model=BaseAPIResponse[dict])
def get_global_version_by_git(commit_sha: str):
    data = version_service.get_global_version_by_commit(commit_sha)
    return BaseAPIResponse(success=True if data else False, message="Success" if data else "Version not found", data=data)

@router.post("/{version_number}/rollback", response_model=BaseAPIResponse[dict])
def rollback_global_version(version_number: int):
    try:
        data = version_service.rollback_global_version(version_number=version_number)
        return BaseAPIResponse(success=True, message="Success", data=data)
    except ValueError as e:
        return BaseAPIResponse(success=False, message=str(e), data=None)

@router.post("/git/{commit_sha}/rollback", response_model=BaseAPIResponse[dict])
def rollback_global_version_by_git(commit_sha: str):
    try:
        data = version_service.rollback_global_version(commit_sha=commit_sha)
        return BaseAPIResponse(success=True, message="Success", data=data)
    except ValueError as e:
        return BaseAPIResponse(success=False, message=str(e), data=None)
