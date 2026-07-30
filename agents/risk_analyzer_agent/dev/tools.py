"""
Tools - Risk Analyzer Agent
==============================
This agent has 2 tools:
  - read_account_summary   (scope: read    - reads the SQLite database)
  - calculate_risk_score   (scope: compute - DETERMINISTIC math, no LLM)

The risk score is calculated deterministically from actual transaction
data in the database. The LLM may explain the result but does not
decide the arithmetic.

IMPORTANT: The risk model here is a DEMO HEURISTIC for governance
demonstration. It is NOT a real financial credit/risk model.
"""

import os
import sys

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(PROJECT_ROOT)

from langchain_core.tools import StructuredTool
from common.db import run_query
from middleware.tool_interceptor import guard_tool
from middleware.policy_loader import load_policy

AGENT_DIR = os.path.join(os.path.dirname(__file__), "..")
POLICY_PATH = os.path.join(AGENT_DIR, "policy.yaml")
policy = load_policy(POLICY_PATH)

# Read agent_id from policy to avoid hardcoded duplication
AGENT_ID = policy.get("agent_id", "risk_analyzer_agent")


# ------------------------------------------------------------------
# Step 1: plain python functions - the real tool logic
# ------------------------------------------------------------------

def _read_account_summary(account_id: int) -> str:
    """
    Read the balance and account type for one account.
    NOTE: Does NOT select customer_name (PII) since this agent's
    policy has pii_allowed=false.
    """
    rows = run_query(
        "SELECT account_id, account_type, balance FROM accounts WHERE account_id = ?",
        (account_id,),
    )
    if not rows:
        return f"No account found with id {account_id}."

    account = rows[0]
    return f"account_id={account['account_id']}, account_type={account['account_type']}, balance={account['balance']}"


def _calculate_risk_score(account_id: int) -> str:
    """
    DETERMINISTIC risk calculation from actual transaction data.

    Steps:
      1. Read the account balance from the database
      2. Sum all negative transactions (outflows) for that account
      3. Calculate risk_score = abs(total_outflow) / balance
      4. Normalize to 0.0 - 1.0 range

    This is a DEMO HEURISTIC, not a real financial risk model.
    The result is a normalized score where:
      0.0 - 0.20 = Low risk
      0.20 - 0.50 = Medium risk
      0.50 - 0.70 = High risk
      0.70 - 1.00 = Critical risk (triggers HITL if enabled)
    """
    # Step 1: Get account balance
    accounts = run_query(
        "SELECT balance FROM accounts WHERE account_id = ?",
        (account_id,),
    )
    if not accounts:
        return (
            '{"error": "Account not found", "account_id": ' +
            str(account_id) + '}'
        )

    balance = accounts[0]["balance"]

    # Step 2: Sum all negative transactions (outflows)
    outflow_rows = run_query(
        "SELECT COALESCE(SUM(ABS(amount)), 0) as total_outflow "
        "FROM transactions WHERE account_id = ? AND amount < 0",
        (account_id,),
    )
    total_outflow = outflow_rows[0]["total_outflow"] if outflow_rows else 0.0

    # Step 3: Calculate ratio
    if balance <= 0:
        risk_score = 1.0
        risk_level = "Critical"
    else:
        ratio = total_outflow / balance
        # Normalize: cap at 1.0
        risk_score = min(ratio, 1.0)

        if risk_score > 0.70:
            risk_level = "Critical"
        elif risk_score > 0.50:
            risk_level = "High"
        elif risk_score > 0.20:
            risk_level = "Medium"
        else:
            risk_level = "Low"

    return (
        f'{{"account_id": {account_id}, '
        f'"balance": {balance}, '
        f'"total_outflow": {total_outflow}, '
        f'"risk_score": {round(risk_score, 4)}, '
        f'"risk_level": "{risk_level}", '
        f'"model": "DEMO_HEURISTIC: outflow/balance ratio"}}'
    )


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
                "(integer) from the finance database. Read-only. Does not "
                "return PII like customer names."
            ),
        ),
        StructuredTool.from_function(
            func=guarded_calculate_risk,
            name="calculate_risk_score",
            description=(
                "Calculate a deterministic risk score for a given account_id "
                "(integer). Reads balance and transactions from the database "
                "and returns a normalized risk score from 0.0 to 1.0. "
                "This is a demo heuristic, not a real financial risk model."
            ),
        ),
    ]
