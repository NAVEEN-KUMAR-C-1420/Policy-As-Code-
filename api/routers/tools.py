from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.services import tool_service

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.get("", response_model=BaseAPIResponse[list])
def list_tools():
    return BaseAPIResponse(success=True, message="Success", data=tool_service.get_all_tools())

@router.get("/{tool_name}", response_model=BaseAPIResponse[dict])
def get_tool_metadata(tool_name: str):
    return BaseAPIResponse(success=True, message="Success", data=tool_service.get_tool_metadata(tool_name))

@router.get("/{tool_name}/usage", response_model=BaseAPIResponse[dict])
def get_tool_usage(tool_name: str):
    return BaseAPIResponse(success=True, message="Success", data=tool_service.get_tool_usage(tool_name))

@router.post("/{tool_name}/test", response_model=BaseAPIResponse[dict])
def test_tool(tool_name: str):
    return BaseAPIResponse(success=True, message="Success", data=tool_service.test_tool_execution(tool_name))
