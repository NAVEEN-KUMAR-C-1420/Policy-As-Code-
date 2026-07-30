"""
Tools - Risk Analyzer Agent
==============================
This agent has 2 tools:
  - read_account_summary   (scope: read    - reads the SQLite database)
  - calculate_risk_score   (scope: compute - pure math, no I/O at all)

Showing a "compute" scope alongside "read" is intentional: it
demonstrates that policy.yaml can tell tools apart by what kind of
access they need, not just a simple allow/deny switch.
"""

import os
import sys

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(PROJECT_ROOT)

from langchain_core.tools import StructuredTool
from common.db import run_query
from middleware.tool_interceptor import guard_tool
from middleware.policy_loader import load_policy

AGENT_ID = "risk_analyzer_agent"
POLICY_PATH = os.path.join(os.path.dirname(__file__), "..", "policy.yaml")
policy = load_policy(POLICY_PATH)


# ------------------------------------------------------------------
# Step 1: plain python functions - the real tool logic
# ------------------------------------------------------------------

def _read_account_summary(account_id: int) -> str:
    """Read the balance and account type for one account."""
    rows = run_query(
        "SELECT account_type, balance FROM accounts WHERE account_id = ?",
        (account_id,),
    )
    if not rows:
        return f"No account found with id {account_id}."

    account = rows[0]
    return f"account_type={account['account_type']}, balance={account['balance']}"


def _calculate_risk_score(balance: float, monthly_outflow: float) -> str:
    """
    A simple, beginner-friendly risk heuristic:
    compares how much money leaves the account each month against
    the current balance. No database or network access - pure math.
    """
    if balance <= 0:
        return "Risk level: High (balance is zero or negative)"

    ratio = monthly_outflow / balance

    if ratio > 0.5:
        risk_level = "High"
    elif ratio > 0.2:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return f"Risk level: {risk_level} (outflow/balance ratio = {round(ratio, 2)})"


# ------------------------------------------------------------------
# Step 2: wrap each function with the governance guard
# ------------------------------------------------------------------

guarded_read_summary = guard_tool(
    tool_name="read_account_summary",
    policy=policy,
    agent_id=AGENT_ID,
    original_function=_read_account_summary,
)

guarded_calculate_risk = guard_tool(
    tool_name="calculate_risk_score",
    policy=policy,
    agent_id=AGENT_ID,
    original_function=_calculate_risk_score,
)


# ------------------------------------------------------------------
# Step 3: expose the guarded functions as LangChain tools
# ------------------------------------------------------------------

def get_tools():
    """Return the list of LangChain tools this agent is allowed to use."""
    return [
        StructuredTool.from_function(
            func=guarded_read_summary,
            name="read_account_summary",
            description=(
                "Read the account_type and balance for a given account_id "
                "(integer) from the finance database. Read-only."
            ),
        ),
        StructuredTool.from_function(
            func=guarded_calculate_risk,
            name="calculate_risk_score",
            description=(
                "Calculate a risk level from balance (float) and "
                "monthly_outflow (float, positive number). Pure computation."
            ),
        ),
    ]
