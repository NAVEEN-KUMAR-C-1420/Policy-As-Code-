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

sys.path.append(os.path.dirname(__file__))

# Make sure the dummy database exists before we query it
from data.init_db import main as init_db
init_db()

from agents.data_collector_agent.dev.tools import guarded_read_transactions
from agents.report_writer_agent.dev.tools import guarded_delete_old_reports

print("\n--- Test 1: ALLOWED tool call ---")
print("Calling read_account_transactions for account 101 "
      "(policy.yaml allows this)...\n")
result_allowed = guarded_read_transactions(account_id=101)
print(result_allowed)

print("\n--- Test 2: BLOCKED tool call ---")
print("Calling delete_old_reports for account 101 "
      "(policy.yaml sets allowed: false for this tool)...\n")
result_blocked = guarded_delete_old_reports(account_id=101)
print(result_blocked)

print("\nDone. Check logs/audit_log.jsonl to see both decisions recorded.")
