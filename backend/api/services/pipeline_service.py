import os
import sys

from core.paths import BASE_DIR as PROJECT_ROOT
sys.path.append(PROJECT_ROOT)

from orchestrator.run_pipeline import run_pipeline as exec_pipeline
from middleware.audit_log import read_recent_entries

def run_pipeline(account_id: int, auto_approve_hitl: bool) -> dict:
    try:
        report = exec_pipeline(account_id, auto_approve_hitl=auto_approve_hitl)
        
        # Get audit logs for this run roughly
        recent_logs = read_recent_entries(20)
        
        return {
            "run_id": f"run_{account_id}_{os.urandom(4).hex()}",
            "status": "completed" if report else "halted_by_hitl",
            "report": report,
            "audit_summary": len(recent_logs)
        }
    except Exception as e:
        raise RuntimeError(f"Pipeline execution failed: {str(e)}")

def run_agent(agent_id: str, input_data: dict) -> dict:
    # A generic runner isn't fully implemented without hardcoding agent modules
    # but we will provide a stub that loads the correct agent module dynamically
    try:
        agent_module = __import__(f"agents.{agent_id}.dev.agent", fromlist=["run"])
        # Very simplified signature unpacking
        if agent_id == "data_collector_agent":
            result = agent_module.run(input_data.get("account_id"))
        elif agent_id == "risk_analyzer_agent":
            result = agent_module.run(input_data.get("account_id"), input_data.get("collected_data"))
        elif agent_id == "report_writer_agent":
            result = agent_module.run(input_data.get("account_id"), input_data.get("collected_data"), input_data.get("risk_report"))
        else:
            raise ValueError("Unknown agent")
        
        return {"agent_id": agent_id, "result": result}
    except Exception as e:
        raise RuntimeError(f"Agent execution failed: {str(e)}")

def get_pipeline_history() -> list:
    return []

def get_pipeline_status(run_id: str) -> dict:
    return {"run_id": run_id, "status": "unknown"}
