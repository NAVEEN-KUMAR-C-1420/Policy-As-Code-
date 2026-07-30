from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.models.requests import PolicyValidateRequest, PolicyDeployRequest, PolicyDiffRequest
from api.services import policy_service

router = APIRouter(prefix="/policies", tags=["Policies"])

@router.get("", response_model=BaseAPIResponse[list])
def list_policies():
    return BaseAPIResponse(success=True, message="Success", data=policy_service.list_policies())

@router.get("/schema", response_model=BaseAPIResponse[dict])
def get_policy_schema():
    return BaseAPIResponse(success=True, message="Success", data=policy_service.get_policy_schema())

@router.get("/{agent_id}", response_model=BaseAPIResponse[dict])
def get_policy(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=policy_service.get_policy(agent_id))

@router.post("/validate", response_model=BaseAPIResponse[dict])
def validate_policy(request: PolicyValidateRequest):
    return BaseAPIResponse(success=True, message="Success", data=policy_service.validate_policy_content(request.policy_yaml_content))

@router.post("/deploy", response_model=BaseAPIResponse[dict])
def deploy_policy(request: PolicyDeployRequest):
    return BaseAPIResponse(success=True, message="Success", data=policy_service.deploy_policy(request.agent_id, request.policy_yaml_content, request.commit_sha))

@router.post("/reload", response_model=BaseAPIResponse[dict])
def reload_policy():
    return BaseAPIResponse(success=True, message="Success", data=policy_service.reload_policy())

@router.post("/diff", response_model=BaseAPIResponse[dict])
def diff_policies(request: PolicyDiffRequest):
    return BaseAPIResponse(success=True, message="Success", data=policy_service.diff_policies(request.agent_id, request.commit_sha))
