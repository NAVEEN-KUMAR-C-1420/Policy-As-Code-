"""
Tools - Data Collector Agent
==============================
Every tool is written in 3 simple steps:

  Step 1: write a plain python function that does the real work
  Step 2: wrap it with guard_tool() so policy.yaml is enforced
  Step 3: expose the wrapped function to LangChain as a Tool

This agent has 2 tools, both READ-ONLY:
  - read_account_transactions  (reads the SQLite database)
  - search_market_news         (reads the web via Tavily)
"""

import os
import sys

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(PROJECT_ROOT)

from langchain_core.tools import StructuredTool
from common.db import run_query
from middleware.tool_interceptor import guard_tool
from middleware.policy_loader import load_policy

AGENT_DIR = os.path.dirname(__file__) / ".."
POLICY_PATH = AGENT_DIR / "policy.yaml"
policy = load_policy(POLICY_PATH)

# Read agent_id from policy to avoid hardcoded duplication
AGENT_ID = policy.get("agent_id", "data_collector_agent")


# ------------------------------------------------------------------
# Step 1: plain python functions - the real tool logic
# ------------------------------------------------------------------

def _read_account_transactions(account_id: int) -> str:
    """
    Read all transactions for one account from the finance database.
    NOTE: Does NOT select customer_name or other PII fields.
    """
    rows = run_query(
        "SELECT txn_date, amount, category, description "
        "FROM transactions WHERE account_id = ?",
        (account_id,),
    )
    if not rows:
        return f"No transactions found for account {account_id}."

    lines = [
        f"{row['txn_date']} | {row['category']} | {row['amount']} | {row['description']}"
        for row in rows
    ]
    return "\n".join(lines)


def _search_market_news(query: str) -> str:
    """Search recent finance/market news for a topic using Tavily."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "TAVILY_API_KEY not set - skipping live news search."

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=3)

        results = response.get("results", [])
        if not results:
            return "No news found."

        lines = [f"- {item.get('title')}: {item.get('url')}" for item in results]
        return "\n".join(lines)
    except Exception as e:
        return f"Market news search failed (degraded gracefully): {e}"


# ------------------------------------------------------------------
# Step 2: wrap each function with the governance guard
# ------------------------------------------------------------------

guarded_read_transactions = guard_tool(
    tool_name="read_account_transactions",
    policy=policy,
    agent_id=AGENT_ID,
    original_function=_read_account_transactions,
)

guarded_search_news = guard_tool(
    tool_name="search_market_news",
    policy=policy,
    agent_id=AGENT_ID,
    original_function=_search_market_news,
)


# ------------------------------------------------------------------
# Step 3: expose the guarded functions as LangChain tools
# ------------------------------------------------------------------

def get_tools():
    """Return the list of LangChain tools this agent is allowed to use."""
    return [
        StructuredTool.from_function(
            func=guarded_read_transactions,
            name="read_account_transactions",
            description=(
                "Read all transactions for a given account_id (integer) "
                "from the finance database. Read-only."
            ),
        ),
        StructuredTool.from_function(
            func=guarded_search_news,
            name="search_market_news",
            description=(
                "Search recent finance/market news for a given topic "
                "string using Tavily. Read-only."
            ),
        ),
    ]
