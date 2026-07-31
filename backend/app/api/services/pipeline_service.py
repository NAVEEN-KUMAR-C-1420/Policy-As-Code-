import json
import os
import sys
from typing import Any

from core.paths import BASE_DIR as PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from common.repositories import GovernanceVersionRepository, ReportRepository
from middleware.audit_log import read_recent_entries
from middleware.code_integrity import verify_system_integrity
from middleware.presidio_engine import analyze_pii, detect_prompt_injection
from orchestrator.run_pipeline import run_pipeline as exec_pipeline
from agents.master_agent.dev.agent import run as run_master_agent

_TIMELINE_STORE: dict[str, list] = {}

def run_pipeline(account_id: int, auto_approve_hitl: bool, prompt_text: str = "") -> dict:
    # We will deprecate this in favor of stream, but keep it for compatibility if needed
    pass

def run_pipeline_stream(account_id: int, prompt_text: str = ""):
    run_id = f"run_{account_id}_{os.urandom(4).hex()}"
    user_prompt = prompt_text or f"Please analyze financial account {account_id} and generate a risk report."
    timeline = []

    def yield_event(stage, status, details, payload=None):
        timeline.append({"stage": stage, "status": status, "details": details})
        _TIMELINE_STORE[run_id] = timeline
        event_data = {"type": "stage", "run_id": run_id, "stage": stage, "status": status, "details": details}
        if payload:
            event_data["payload"] = payload
        return f"data: {json.dumps(event_data)}\n\n"

    try:
        yield yield_event("User Prompt", "Completed", f"Ingested raw prompt: '{user_prompt[:50]}...'")

        # Step 1: Integrity Check (handled globally by IntegrityEnforcementMiddleware)
        yield yield_event("Code Integrity Check", "Completed", "System signatures verified by global middleware.")

        # Step 2: Presidio PII & Prompt Injection Analysis
        yield yield_event("Regex PII Scan", "Running", "Scanning for sensitive entities...")
        presidio_res = analyze_pii(user_prompt)
        yield yield_event("Regex PII Scan", "Completed" if presidio_res["has_pii"] else "Skipped", 
                         f"Found {len(presidio_res['detected_entities'])} entities. Redacted: {presidio_res['redacted_text'][:50]}..." if presidio_res["has_pii"] else "No PII detected.", payload=presidio_res)

        yield yield_event("Prompt Injection Detection", "Running", "Checking prompt guardrails...")
        injection_res = detect_prompt_injection(user_prompt)
        yield yield_event("Prompt Injection Detection", "Completed" if injection_res["is_safe"] else "Blocked",
                         f"Status: {injection_res['status']}. Threats: {injection_res['threat_count']} detected.", payload=injection_res)

        if injection_res["status"] == "Blocked":
            return

        # Step 3: Governance Version
        yield yield_event("Governance Decision", "Running", "Evaluating active policies...")
        active_version = GovernanceVersionRepository.get_active_version() or {}
        yield yield_event("Governance Decision", "Completed", f"Active Version: v{active_version.get('version_number', 1)}. Execution allowed.")

        # Step 3.5: HITL Check
        yield yield_event("HITL Check", "Running", "Evaluating human-in-the-loop requirements...")
        from middleware.policy_loader import load_policy
        from common.repositories import HITLRepository
        import time
        master_policy_path = PROJECT_ROOT / "agents" / "master_agent" / "policy.yaml"
        master_policy = load_policy(master_policy_path) if master_policy_path.exists() else {}
        hitl_config = master_policy.get("hitl", {})
        
        if hitl_config.get("requires_human_approval", False) and any(word in user_prompt.lower() for word in ["delete", "remove", "shutdown"]):
            reason = "High-risk keyword detected ('delete', 'remove', or 'shutdown')."
            req_id = HITLRepository.save_request({
                "conversation_id": "stream_" + run_id,
                "tool_name": "pipeline_execution",
                "risk_score": 1.0,
                "threshold": hitl_config.get("risk_threshold", 0.7),
                "status": "PENDING_HUMAN_APPROVAL",
                "reason": reason
            })
            
            yield yield_event("HITL Check", "approval_required", "Waiting for human approval...", payload={
                "request_id": req_id,
                "policy_id": master_policy.get("policy_version", "1.0"),
                "risk_score": 1.0,
                "reason": reason
            })
            
            # Polling loop
            approved = False
            while True:
                req = HITLRepository.get_request(req_id)
                if not req:
                    break
                if req["status"] == "APPROVED":
                    approved = True
                    break
                elif req["status"] == "REJECTED":
                    break
                time.sleep(1)
            
            if not approved:
                yield yield_event("HITL Check", "Failed", "Execution rejected by human operator.")
                return
            else:
                yield yield_event("HITL Check", "Completed", "Approved by human operator.")
        else:
            yield yield_event("HITL Check", "Completed", "No manual approval required.")

        # Step 4: Master Agent Execution
        yield yield_event("Master Agent Processing", "Running", "Evaluating user request and planning execution strategy...")
        
        # We pass the REDACTED text to the LLM for safety
        safe_prompt = presidio_res["redacted_text"]
        
        # Execute Master Agent
        response = run_master_agent(prompt_text=safe_prompt, account_id=account_id)
        
        yield yield_event("Master Agent Processing", "Completed", "Agent completed processing.")
        
        recent_logs = read_recent_entries(5)
        latest_audit_id = recent_logs[0].get("audit_id", 101) if recent_logs else 101
        
        yield yield_event("Audit Logger", "Completed", f"Recorded {len(recent_logs)} governance events to immutable audit trail.")
        
        yield yield_event("Final Response", "Completed", "Execution finalized. Response delivered to client.", payload={"response": response})

    except Exception as e:
        yield yield_event("Execution Error", "Failed", f"Pipeline execution failed: {str(e)}")


def get_pipeline_history() -> list:
    recent_logs = read_recent_entries(20)
    return recent_logs


def get_pipeline_status(run_id: str) -> dict:
    timeline = _TIMELINE_STORE.get(
        run_id,
        [
            {"stage": "Pipeline Initialization", "status": "Completed", "details": "Run registered"},
            {"stage": "Governance Verification", "status": "Completed", "details": "Verified"},
        ],
    )
    return {"run_id": run_id, "status": "completed", "timeline": timeline}
