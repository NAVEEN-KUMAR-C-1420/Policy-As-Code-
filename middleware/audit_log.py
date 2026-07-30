"""
Audit Log
==========
Every governance decision - whether ALLOWED, DENIED, RATE_LIMITED,
or other events like MODEL_DENIED, HITL_REQUIRED, etc. - gets written
here as one JSON line.

This gives a complete, readable trail for AI governance review.

The log file lives at: logs/audit_log.jsonl

Event types recorded:
  - TOOL_CALL          (with decision: ALLOWED / DENIED / RATE_LIMITED)
  - MODEL_CHECK        (with decision: ALLOWED / MODEL_DENIED)
  - HITL_CHECK         (with decision: ALLOWED / HITL_REQUIRED)
  - POLICY_VALIDATION  (with decision: POLICY_VALIDATION_FAILED / ALLOWED)
  - STARTUP            (agent startup events)

IMPORTANT: This module never logs API keys, secrets, or raw PII.
"""

import json
import os
from datetime import datetime, timezone

LOG_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "logs", "audit_log.jsonl"
)


def write_audit_entry(entry: dict):
    """
    Append one audit entry to the JSONL log file.

    'entry' should be a dictionary with fields like:
        agent_id, event_type, tool_name, scope, decision, reason

    A UTC timestamp is automatically added.
    """
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

    entry["timestamp"] = datetime.now(timezone.utc).isoformat()

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_recent_entries(n: int = 50) -> list:
    """
    Read the last N entries from the audit log.
    Returns a list of dictionaries (most recent last).
    Useful for testing and verification.
    """
    if not os.path.exists(LOG_FILE_PATH):
        return []

    entries = []
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return entries[-n:]
