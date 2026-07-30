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
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from langchain_core.tools import StructuredTool

from common.db import run_write
from middleware.policy_loader import load_policy
from middleware.tool_interceptor import guard_tool

AGENT_DIR = Path(__file__).resolve().parent.parent
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
    """Delete all saved reports for an account. Governed by policy."""
    run_write("DELETE FROM reports WHERE account_id = ?", (account_id,))
    return f"All reports deleted for account {account_id}."

def _send_investor_email(email_address: str, content: str) -> str:
    """Send an email to an investor with financial data."""
    return f"Successfully sent email to {email_address}."

def _export_database(format: str) -> str:
    """Export the entire database to a file."""
    return f"Database exported successfully in {format} format."

def _access_sensitive_data(query: str) -> str:
    """Query highly sensitive internal data bypassing normal filters."""
    return f"Sensitive data retrieved for query: {query}"


# ------------------------------------------------------------------
# Step 2: wrap each function with the governance guard
# ------------------------------------------------------------------

guarded_save_to_db = guard_tool(tool_name="save_report_to_db", policy=policy, agent_id=AGENT_ID, original_function=_save_report_to_db)
guarded_write_file = guard_tool(tool_name="write_report_file", policy=policy, agent_id=AGENT_ID, original_function=_write_report_file)
guarded_delete_old_reports = guard_tool(tool_name="delete_old_reports", policy=policy, agent_id=AGENT_ID, original_function=_delete_old_reports)
guarded_send_investor_email = guard_tool(tool_name="send_investor_email", policy=policy, agent_id=AGENT_ID, original_function=_send_investor_email)
guarded_export_database = guard_tool(tool_name="export_database", policy=policy, agent_id=AGENT_ID, original_function=_export_database)
guarded_access_sensitive_data = guard_tool(tool_name="access_sensitive_data", policy=policy, agent_id=AGENT_ID, original_function=_access_sensitive_data)


# ------------------------------------------------------------------
# Step 3: expose ALL tools to LangChain so governance can intercept them
# ------------------------------------------------------------------

def get_tools():
    """Return the list of LangChain tools this agent is allowed to use."""
    return [
        StructuredTool.from_function(func=guarded_save_to_db, name="save_report_to_db", description="Save a report summary (string) to the database for a given account_id (integer)."),
        StructuredTool.from_function(func=guarded_write_file, name="write_report_file", description="Write the full report content (string) to a markdown file for a given account_id (integer)."),
        StructuredTool.from_function(func=guarded_delete_old_reports, name="delete_old_reports", description="Delete all historical reports for a given account_id (integer)."),
        StructuredTool.from_function(func=guarded_send_investor_email, name="send_investor_email", description="Send an email to an investor with financial data (email_address, content)."),
        StructuredTool.from_function(func=guarded_export_database, name="export_database", description="Export the entire database to a file (format: str)."),
        StructuredTool.from_function(func=guarded_access_sensitive_data, name="access_sensitive_data", description="Query highly sensitive internal data bypassing normal filters (query: str)."),
    ]
