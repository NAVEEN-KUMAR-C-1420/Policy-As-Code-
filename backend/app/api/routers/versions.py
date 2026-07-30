from fastapi import APIRouter

from api.models.requests import PolicyRollbackRequest
from api.models.responses import BaseAPIResponse
from api.services import version_service

router = APIRouter(prefix="/policies/{agent_id}", tags=["Versions"])


@router.get("/versions", response_model=BaseAPIResponse[list])
def list_versions(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=version_service.get_versions(agent_id))


@router.get("/versions/{commit_sha}", response_model=BaseAPIResponse[dict])
def get_historical_policy(agent_id: str, commit_sha: str):
    return BaseAPIResponse(
        success=True, message="Success", data=version_service.get_historical_policy(agent_id, commit_sha)
    )


@router.post("/rollback", response_model=BaseAPIResponse[dict])
def rollback_policy(agent_id: str, request: PolicyRollbackRequest):
    return BaseAPIResponse(
        success=True, message="Success", data=version_service.rollback_policy(agent_id, request.commit_sha)
    )
