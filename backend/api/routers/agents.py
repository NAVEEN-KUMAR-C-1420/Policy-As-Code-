from fastapi import APIRouter

from api.models.requests import AgentRunRequest
from api.models.responses import BaseAPIResponse
from api.services import agent_service, pipeline_service

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=BaseAPIResponse[list])
def list_agents():
    return BaseAPIResponse(success=True, message="Success", data=agent_service.list_agents())


@router.get("/{agent_id}", response_model=BaseAPIResponse[dict])
def get_agent_details(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=agent_service.get_agent_details(agent_id))


@router.get("/{agent_id}/status", response_model=BaseAPIResponse[dict])
def get_agent_status(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=agent_service.get_agent_status(agent_id))


@router.get("/{agent_id}/tools", response_model=BaseAPIResponse[list])
def get_agent_tools(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=agent_service.get_agent_tools(agent_id))


@router.get("/{agent_id}/policy", response_model=BaseAPIResponse[dict])
def get_agent_policy(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=agent_service.get_agent_policy(agent_id))


@router.get("/{agent_id}/config", response_model=BaseAPIResponse[dict])
def get_agent_config(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=agent_service.get_agent_config(agent_id))


@router.post("/{agent_id}/reload", response_model=BaseAPIResponse[dict])
def reload_agent_config(agent_id: str):
    return BaseAPIResponse(success=True, message="Success", data=agent_service.reload_agent_config(agent_id))


@router.post("/{agent_id}/run", response_model=BaseAPIResponse[dict])
def run_agent(agent_id: str, request: AgentRunRequest):
    return BaseAPIResponse(
        success=True, message="Success", data=pipeline_service.run_agent(agent_id, request.input_data)
    )
