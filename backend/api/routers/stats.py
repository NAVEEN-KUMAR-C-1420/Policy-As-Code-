from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.services import stats_service

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("", response_model=BaseAPIResponse[dict])
def get_stats():
    return BaseAPIResponse(success=True, message="Success", data=stats_service.get_overall_stats())

@router.get("/agents", response_model=BaseAPIResponse[dict])
def get_agent_stats():
    return BaseAPIResponse(success=True, message="Success", data=stats_service.get_agent_stats())

@router.get("/tools", response_model=BaseAPIResponse[dict])
def get_tool_stats():
    return BaseAPIResponse(success=True, message="Success", data=stats_service.get_tool_stats())

@router.get("/policies", response_model=BaseAPIResponse[dict])
def get_policy_stats():
    return BaseAPIResponse(success=True, message="Success", data=stats_service.get_policy_stats())
