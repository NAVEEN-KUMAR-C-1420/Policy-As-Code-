import os
import sys
from pathlib import Path

from core.paths import BASE_DIR as PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from middleware.audit_log import read_recent_entries


def get_recent_logs(limit: int = 50) -> list:
    return read_recent_entries(limit)


def get_logs_for_run(run_id: str) -> list:
    # We simulate run filtering by just getting recent logs
    return read_recent_entries(50)


def search_logs(event_type: str = None, agent_id: str = None, decision: str = None, limit: int = 50) -> list:
    logs = read_recent_entries(limit)
    if event_type:
        logs = [log for log in logs if log.get("event_type") == event_type]
    if agent_id:
        logs = [log for log in logs if log.get("agent_id") == agent_id]
    if decision:
        logs = [log for log in logs if log.get("decision") == decision]
    return logs

from core.paths import LOG_DIR

def export_logs() -> str:
    log_file = LOG_DIR / "audit_log.jsonl"
    if not Path(log_file).exists():
        # Create it if it doesn't exist for test environment
        log_file.touch(exist_ok=True)
    with open(log_file, "r", encoding="utf-8") as f:
        return f.read()
