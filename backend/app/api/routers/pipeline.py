from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.models.requests import PipelineRunRequest
from api.models.responses import BaseAPIResponse
from api.services import pipeline_service

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.post("/run", response_model=BaseAPIResponse[dict])
def run_pipeline(request: PipelineRunRequest):
    return BaseAPIResponse(
        success=True,
        message="Success",
        data=pipeline_service.run_pipeline(request.account_id, request.auto_approve_hitl),
    )

@router.get("/stream")
def stream_pipeline(account_id: int = 0, prompt: str = ""):
    return StreamingResponse(
        pipeline_service.run_pipeline_stream(account_id, prompt), 
        media_type="text/event-stream"
    )


@router.get("/history", response_model=BaseAPIResponse[list])
def get_pipeline_history():
    return BaseAPIResponse(success=True, message="Success", data=pipeline_service.get_pipeline_history())


@router.get("/status/{run_id}", response_model=BaseAPIResponse[dict])
def get_pipeline_status(run_id: str):
    return BaseAPIResponse(success=True, message="Success", data=pipeline_service.get_pipeline_status(run_id))
