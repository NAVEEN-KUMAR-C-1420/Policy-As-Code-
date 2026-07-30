from fastapi import APIRouter

from api.models.responses import BaseAPIResponse

router = APIRouter(prefix="/architecture", tags=["Architecture"])

ARCHITECTURE_GRAPH = {
    "nodes": [
        {"id": "user", "label": "User / Evaluator", "type": "client"},
        {"id": "react", "label": "React Frontend", "type": "frontend"},
        {"id": "fastapi", "label": "FastAPI REST Server", "type": "api"},
        {"id": "presidio", "label": "Presidio PII Engine", "type": "security"},
        {"id": "injection", "label": "Prompt Injection Shield", "type": "security"},
        {"id": "governance", "label": "Governance Middleware", "type": "middleware"},
        {"id": "integrity", "label": "Code Integrity Engine", "type": "middleware"},
        {"id": "policy", "label": "Policy Validator & Hash", "type": "governance"},
        {"id": "version", "label": "Governance Version Engine", "type": "governance"},
        {"id": "orchestrator", "label": "Agent Orchestrator", "type": "core"},
        {"id": "data_collector", "label": "Data Collector Agent", "type": "agent"},
        {"id": "risk_analyzer", "label": "Risk Analyzer Agent", "type": "agent"},
        {"id": "report_writer", "label": "Report Writer Agent", "type": "agent"},
        {"id": "audit", "label": "Audit Trail Logger", "type": "logging"},
        {"id": "supabase", "label": "Supabase / SQLite Storage", "type": "database"},
    ],
    "links": [
        {"source": "user", "target": "react"},
        {"source": "react", "target": "fastapi"},
        {"source": "fastapi", "target": "presidio"},
        {"source": "presidio", "target": "injection"},
        {"source": "injection", "target": "integrity"},
        {"source": "integrity", "target": "governance"},
        {"source": "governance", "target": "policy"},
        {"source": "policy", "target": "version"},
        {"source": "version", "target": "orchestrator"},
        {"source": "orchestrator", "target": "data_collector"},
        {"source": "data_collector", "target": "risk_analyzer"},
        {"source": "risk_analyzer", "target": "report_writer"},
        {"source": "report_writer", "target": "audit"},
        {"source": "audit", "target": "supabase"},
    ],
}


@router.get("", response_model=BaseAPIResponse[dict])
def get_architecture():
    return BaseAPIResponse(success=True, message="Success", data=ARCHITECTURE_GRAPH)
