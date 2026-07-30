"""
Policy Enforcement Demo / Test
=================================
This script proves the governance middleware works WITHOUT needing
any LLM API keys, because it calls the guarded tool functions
directly instead of going through an agent.

Run it with:
    python test_policy_enforcement.py

What it shows:
  1. An ALLOWED tool call  -> passes policy.yaml, runs, gets logged
  2. A BLOCKED tool call   -> denied by policy.yaml, never runs, gets logged

After running, open logs/audit_log.jsonl to see both decisions recorded.
"""

import os
import sys

# Ensure PROJECT_ROOT is reachable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from data.init_db import main as init_db
init_db()

from agents.data_collector_agent.dev.tools import guarded_read_transactions
from agents.report_writer_agent.dev.tools import guarded_delete_old_reports

def test_allowed_tool_call():
    """Test that an ALLOWED tool call passes policy.yaml and runs."""
    result = guarded_read_transactions(account_id=101)
    assert result is not None
    assert "BLOCKED BY POLICY" not in str(result)

def test_blocked_tool_call():
    """Test that a BLOCKED tool call is denied by policy.yaml and never runs."""
    result = guarded_delete_old_reports(account_id=101)
    assert result is not None
    assert "BLOCKED BY POLICY" in str(result)
