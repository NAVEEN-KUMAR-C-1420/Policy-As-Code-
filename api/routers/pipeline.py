from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.models.requests import PipelineRunRequest
from api.services import pipeline_service

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])

@router.post("/run", response_model=BaseAPIResponse[dict])
def run_pipeline(request: PipelineRunRequest):
    return BaseAPIResponse(success=True, message="Success", data=pipeline_service.run_pipeline(request.account_id, request.auto_approve_hitl))

@router.get("/history", response_model=BaseAPIResponse[list])
def get_pipeline_history():
    return BaseAPIResponse(success=True, message="Success", data=pipeline_service.get_pipeline_history())

@router.get("/status/{run_id}", response_model=BaseAPIResponse[dict])
def get_pipeline_status(run_id: str):
    return BaseAPIResponse(success=True, message="Success", data=pipeline_service.get_pipeline_status(run_id))
