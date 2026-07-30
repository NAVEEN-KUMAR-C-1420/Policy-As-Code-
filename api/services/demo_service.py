import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from data.init_db import main as init_db
from orchestrator.run_pipeline import run_pipeline

def run_sample() -> dict:
    report = run_pipeline(account_id=101, auto_approve_hitl=True)
    return {"status": "demo completed", "report": report}

def trigger_policy_violation() -> dict:
    from agents.report_writer_agent.dev.tools import guarded_delete_old_reports
    result = guarded_delete_old_reports(account_id=101)
    return {"status": "violation triggered", "result": result}

def reset_demo() -> dict:
    init_db()
    return {"status": "demo reset"}

def load_sample_data() -> dict:
    init_db()
    return {"status": "sample data loaded"}
