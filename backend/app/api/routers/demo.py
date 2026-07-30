from fastapi import APIRouter
from pydantic import BaseModel

from api.models.responses import BaseAPIResponse
from api.services import demo_service

router = APIRouter(prefix="/demo", tags=["Demo"])


class ToolToggleRequest(BaseModel):
    tool_key: str
    enabled: bool


class SafeModeToggleRequest(BaseModel):
    enabled: bool


@router.get("/tools", response_model=BaseAPIResponse[list])
def get_demo_tools():
    return BaseAPIResponse(success=True, message="Success", data=demo_service.get_demo_tools())


@router.post("/tool/toggle", response_model=BaseAPIResponse[dict])
def toggle_demo_tool(request: ToolToggleRequest):
    return BaseAPIResponse(
        success=True,
        message="Tool state updated",
        data=demo_service.toggle_demo_tool(request.tool_key, request.enabled),
    )


@router.post("/safemode/toggle", response_model=BaseAPIResponse[dict])
def toggle_safemode(request: SafeModeToggleRequest):
    return BaseAPIResponse(
        success=True, message="Safe Mode toggled", data=demo_service.toggle_safemode(request.enabled)
    )


@router.post("/run-sample", response_model=BaseAPIResponse[dict])
def run_sample():
    return BaseAPIResponse(success=True, message="Success", data=demo_service.run_sample())


@router.post("/policy-violation", response_model=BaseAPIResponse[dict])
def trigger_policy_violation():
    return BaseAPIResponse(success=True, message="Success", data=demo_service.trigger_policy_violation())


@router.post("/reset", response_model=BaseAPIResponse[dict])
def reset_demo():
    return BaseAPIResponse(success=True, message="Success", data=demo_service.reset_demo())


@router.post("/load-sample-data", response_model=BaseAPIResponse[dict])
def load_sample_data():
    return BaseAPIResponse(success=True, message="Success", data=demo_service.load_sample_data())
