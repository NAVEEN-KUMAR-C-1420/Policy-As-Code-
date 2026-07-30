from core.paths import REPORT_DIR
"""
Tools - Report Writer Agent
==============================
This agent has 3 tools defined here, but only 2 are ever handed to
the LLM (see get_tools() at the bottom):

  - save_report_to_db    (scope: write)  -> given to the LLM
  - write_report_file    (scope: write)  -> given to the LLM
  - delete_old_reports    (scope: delete) -> NOT given to the LLM,
                                             and blocked by policy.yaml
                                             even if it were called directly.

delete_old_reports exists on purpose, as a governance demonstration:
see the test suite to watch it get blocked and logged.
"""

import os
import sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(PROJECT_ROOT)

from langchain_core.tools import StructuredTool
from common.db import run_write
from middleware.tool_interceptor import guard_tool
from middleware.policy_loader import load_policy

AGENT_DIR = os.path.dirname(__file__) / ".."
POLICY_PATH = AGENT_DIR / "policy.yaml"
policy = load_policy(POLICY_PATH)

# Read agent_id from policy to avoid hardcoded duplication
AGENT_ID = policy.get("agent_id", "report_writer_agent")

REPORTS_DIR = REPORT_DIR


# ------------------------------------------------------------------
# Step 1: plain python functions - the real tool logic
# ------------------------------------------------------------------

def _save_report_to_db(account_id: int, summary: str) -> str:
    """Insert a new report row into the reports table."""
    run_write(
        "INSERT INTO reports (account_id, created_at, summary) VALUES (?, ?, ?)",
        (account_id, datetime.now(timezone.utc).isoformat(), summary),
    )
    return f"Report saved to database for account {account_id}."


from common.repositories import ReportRepository

def _write_report_file(account_id: int, content: str) -> str:
    """Store the full report content (markdown string) in the database via the repository."""
    ReportRepository.save_report_content(account_id, content, generated_by=AGENT_ID)
    return f"Report saved to database for account {account_id}."


def _delete_old_reports(account_id: int) -> str:
    """
    DANGEROUS on purpose: deletes all saved reports for an account.
    policy.yaml marks this tool as allowed: false AND its scope
    (delete) is in denied_scopes, so guard_tool() should always
    block it before this code ever runs.
    """
    run_write("DELETE FROM reports WHERE account_id = ?", (account_id,))
    return f"All reports deleted for account {account_id}."


# ------------------------------------------------------------------
# Step 2: wrap each function with the governance guard
# ------------------------------------------------------------------

guarded_save_to_db = guard_tool(
    tool_name="save_report_to_db",
    policy=policy,
    agent_id=AGENT_ID,
    original_function=_save_report_to_db,
)

guarded_write_file = guard_tool(
    tool_name="write_report_file",
    policy=policy,
    agent_id=AGENT_ID,
    original_function=_write_report_file,
)

# This one is still wrapped (so it still gets checked + logged if ever
# called directly), but it is deliberately left out of get_tools()
# below so the LLM agent never even sees it as an option.
guarded_delete_old_reports = guard_tool(
    tool_name="delete_old_reports",
    policy=policy,
    agent_id=AGENT_ID,
    original_function=_delete_old_reports,
)


# ------------------------------------------------------------------
# Step 3: expose only the allowed tools to LangChain
# ------------------------------------------------------------------

def get_tools():
    """Return the list of LangChain tools this agent is allowed to use."""
    return [
        StructuredTool.from_function(
            func=guarded_save_to_db,
            name="save_report_to_db",
            description=(
                "Save a report summary (string) to the database for a "
                "given account_id (integer)."
            ),
        ),
        StructuredTool.from_function(
            func=guarded_write_file,
            name="write_report_file",
            description=(
                "Write the full report content (string) to a markdown "
                "file for a given account_id (integer)."
            ),
        ),
    ]
