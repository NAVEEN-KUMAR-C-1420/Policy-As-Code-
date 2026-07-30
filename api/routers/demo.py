from fastapi import APIRouter
from api.models.responses import BaseAPIResponse
from api.services import demo_service

router = APIRouter(prefix="/demo", tags=["Demo"])

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
