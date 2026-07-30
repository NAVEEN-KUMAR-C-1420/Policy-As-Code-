"""
Sequential Pipeline Orchestrator
===================================
Runs the 3 agents ONE AFTER ANOTHER in a fixed order:

    Data Collector Agent -> Risk Analyzer Agent -> Report Writer Agent

This is plain Python sequential execution using LangChain agents -
it does NOT use LangGraph. Each agent's text output is simply passed
in as part of the next agent's input message.

Governance is enforced at every stage:
  - Agent/policy compatibility is validated before LLM creation
  - Tool calls are governed by policy at runtime
  - Risk score triggers HITL check before proceeding
  - Audit log records all governance decisions

Usage:
    python orchestrator/run_pipeline.py
"""

import os
import sys
import json

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()  # loads GROQ_API_KEY, TAVILY_API_KEY, etc. from .env

from agents.data_collector_agent.dev.agent import run as run_data_collector
from agents.risk_analyzer_agent.dev.agent import run as run_risk_analyzer
from agents.report_writer_agent.dev.agent import run as run_report_writer
from agents.risk_analyzer_agent.dev.tools import _calculate_risk_score
from middleware.policy_loader import load_policy
from middleware.hitl import check_hitl, request_cli_approval


def run_pipeline(account_id, auto_approve_hitl=False):
    """
    Run the full 3-agent pipeline with governance enforcement.

    Parameters:
        account_id       - the account to analyze (e.g., 101, 102, 103)
        auto_approve_hitl - if True, skip CLI prompt for HITL (for testing)

    Returns the final report text, or None if blocked by HITL.
    """
    print(f"\n{'='*60}")
    print(f"  FINANCIAL ANALYSIS PIPELINE - Account {account_id}")
    print(f"{'='*60}")

    # ---- STEP 1: Data Collector Agent ----
    print(f"\n=== STEP 1: Data Collector Agent (account {account_id}) ===")
    collected_data = run_data_collector(account_id)
    print(collected_data)

    # ---- STEP 2: Risk Analyzer Agent ----
    print("\n=== STEP 2: Risk Analyzer Agent ===")
    risk_report = run_risk_analyzer(account_id, collected_data)
    print(risk_report)

    # ---- HITL CHECK: Deterministic risk calculation for governance ----
    print("\n=== HITL GOVERNANCE CHECK ===")
    # Run the deterministic risk calculation directly (not through LLM)
    risk_result_str = _calculate_risk_score(account_id)
    try:
        risk_result = json.loads(risk_result_str)
        risk_score = risk_result.get("risk_score", 0.0)
    except (json.JSONDecodeError, TypeError):
        risk_score = 0.0
        print(f"  Warning: Could not parse risk result, using score 0.0")

    risk_policy_path = os.path.join(
        PROJECT_ROOT, "agents", "risk_analyzer_agent", "policy.yaml"
    )
    risk_policy = load_policy(risk_policy_path)
    hitl_result = check_hitl(
        risk_score=risk_score,
        policy=risk_policy,
        agent_id="risk_analyzer_agent",
    )

    print(f"  Risk Score: {risk_score:.2f}")
    print(f"  HITL Status: {hitl_result['status']}")

    if hitl_result["approval_required"]:
        if auto_approve_hitl:
            print("  Auto-approved for testing (auto_approve_hitl=True)")
        else:
            approved = request_cli_approval(hitl_result)
            if not approved:
                print("\n  Pipeline STOPPED: Human operator rejected high-risk operation.")
                return None

    # ---- STEP 3: Report Writer Agent ----
    print("\n=== STEP 3: Report Writer Agent ===")
    final_report = run_report_writer(account_id, collected_data, risk_report)
    print(final_report)

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE for Account {account_id}")
    print(f"{'='*60}\n")

    return final_report


if __name__ == "__main__":
    # Dummy accounts available: 101, 102, 103 (see data/init_db.py)
    ACCOUNT_ID = 101
    run_pipeline(ACCOUNT_ID)
