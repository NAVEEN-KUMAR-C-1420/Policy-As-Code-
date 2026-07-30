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

from common.repositories import AuditRepository


def write_audit_entry(entry: dict):
    """
    Store one audit entry into the database.

    'entry' should be a dictionary with fields like:
        agent_id, event_type, tool_name, scope, decision, reason
    """
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Supabase uses JSON fields, but our schema expects stringification if metadata.
    # The repository handles the SQL insert.
    AuditRepository.save(entry)


def read_recent_entries(n: int = 50) -> list:
    """
    Read the last N entries from the audit log database.
    """
    rows = AuditRepository.get_recent(limit=n)

    # Re-map DB row fields back to the expected dictionary formats for testing backwards compatibility.
    entries = []
    for row in rows:
        parsed = dict(row)
        if "action" in parsed and parsed["action"]:
            parsed["event_type"] = parsed["action"]
        if "agent_name" in parsed and parsed["agent_name"]:
            parsed["agent_id"] = parsed["agent_name"]
        if "metadata" in parsed and parsed["metadata"]:
            try:
                parsed["metadata"] = json.loads(parsed["metadata"])
            except Exception:
                pass
        entries.append(parsed)

    # Re-reverse to put oldest first, as previous logic did (it read file top to bottom and took last N)
    return entries[::-1]
