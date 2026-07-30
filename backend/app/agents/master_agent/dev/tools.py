import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from langchain_core.tools import StructuredTool
from middleware.tool_interceptor import guard_tool
from orchestrator.run_pipeline import run_pipeline as exec_pipeline
from middleware.policy_loader import load_policy

AGENT_DIR = Path(__file__).resolve().parent.parent
POLICY_PATH = AGENT_DIR / "policy.yaml"
policy = load_policy(POLICY_PATH)
AGENT_ID = policy.get("agent_id", "master_agent")


def _run_subagent_pipeline(account_id: int) -> str:
    """
    Kicks off the subagent pipeline for the given account_id.
    This runs the Data Collector, Risk Analyzer, and Report Writer in sequence.
    """
    try:
        # We pass auto_approve_hitl=True since this is a background process triggered by the Master Agent.
        report = exec_pipeline(account_id, auto_approve_hitl=True)
        return f"Successfully generated report:\n\n{report}"
    except Exception as e:
        return f"Pipeline execution failed: {str(e)}"

guarded_run_subagent_pipeline = guard_tool(
    tool_name="run_subagent_pipeline",
    policy=policy,
    agent_id=AGENT_ID,
    original_function=_run_subagent_pipeline,
)


def get_tools() -> list:
    return [
        StructuredTool.from_function(
            func=guarded_run_subagent_pipeline,
            name="run_subagent_pipeline",
            description=(
                "Kicks off the subagent pipeline for the given account_id. "
                "This runs the Data Collector, Risk Analyzer, and Report Writer in sequence."
            ),
        )
    ]
