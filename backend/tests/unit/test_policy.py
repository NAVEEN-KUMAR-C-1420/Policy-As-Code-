"""
Policy Enforcement Demo / Test
=================================
This script proves the governance middleware works WITHOUT needing
any LLM API keys, because it calls the guarded tool functions
directly instead of going through an agent.

Run it with:
    python -m pytest tests/unit/test_policy.py -v

What it shows:
  1. An ALLOWED tool call  -> passes policy.yaml, runs, gets logged
  2. A BLOCKED tool call   -> denied by policy.yaml, never runs, gets logged

After running, open logs/audit_log.jsonl to see both decisions recorded.
"""

import os
import sys

# Ensure PROJECT_ROOT is reachable
from core.paths import BASE_DIR as PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# NOTE: Database initialization is handled by conftest.py session fixture.

from agents.data_collector_agent.dev.tools import guarded_read_transactions
from middleware.tool_interceptor import guard_tool

# Create a dummy blocked tool for testing
def _dummy_blocked_tool(account_id: int) -> str:
    return "This should not run."

# We pass agent_id="report_writer_agent" which has a policy that denies 'delete' scope tools.
# Wait, actually report_writer_agent explicitly denies 'delete_old_reports'.
# Let's load that policy.
from middleware.policy_loader import load_policy
from core.paths import AGENTS_DIR
policy = load_policy(AGENTS_DIR / "report_writer_agent" / "policy.yaml")

guarded_dummy_blocked = guard_tool(
    tool_name="delete_old_reports",
    policy=policy,
    agent_id="report_writer_agent",
    original_function=_dummy_blocked_tool
)


def test_allowed_tool_call():
    """Test that an ALLOWED tool call passes policy.yaml and runs."""
    result = guarded_read_transactions(account_id=101)
    assert result is not None
    assert "BLOCKED BY POLICY" not in str(result)


def test_blocked_tool_call():
    """Test that a BLOCKED tool call is denied by policy.yaml and never runs."""
    result = guarded_dummy_blocked(account_id=101)
    assert result is not None
    assert "BLOCKED BY POLICY" in str(result)
