"""
Audit Log
==========
Every tool call - whether it was ALLOWED or BLOCKED by policy - gets
written here as one JSON line. This gives you a complete, readable
trail for AI governance review.

The log file lives at: logs/audit_log.jsonl
"""

import json
import os
from datetime import datetime

LOG_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "logs", "audit_log.jsonl"
)


def write_audit_entry(entry: dict):
    """
    Append one audit entry to the log file.
    'entry' should be a small dictionary, e.g.:
        {"agent_id": "...", "tool_name": "...", "decision": "ALLOWED"}
    """
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

    entry["timestamp"] = datetime.utcnow().isoformat()

    with open(LOG_FILE_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
