import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from core.paths import AGENTS_DIR
from core.paths import BASE_DIR as PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from api.services.version_service import check_and_create_version_on_startup
from data.init_db import main as init_db
from middleware.audit_log import write_audit_entry
from middleware.code_integrity import set_safe_mode_override, verify_system_integrity
from orchestrator.run_pipeline import run_pipeline

# Hardcoded demo tool state for demonstration
DEMO_TOOLS_STATE = {
    "delete_financial_report": {
        "name": "Delete Financial Report",
        "key": "delete_old_reports",
        "agent_id": "report_writer_agent",
        "allowed": False,
        "scope": "delete",
        "description": "Deletes historical account financial reports from database.",
    },
    "send_investor_email": {
        "name": "Send Investor Email",
        "key": "send_investor_email",
        "agent_id": "report_writer_agent",
        "allowed": False,
        "scope": "external_communication",
        "description": "Dispatches unverified financial summaries to external investor mailing lists.",
    },
    "export_database": {
        "name": "Export Database",
        "key": "export_database",
        "agent_id": "report_writer_agent",
        "allowed": False,
        "scope": "system_export",
        "description": "Exports the entire SQLite/PostgreSQL database to a file format.",
    },
    "access_sensitive_data": {
        "name": "Access Sensitive Data",
        "key": "access_sensitive_data",
        "agent_id": "report_writer_agent",
        "allowed": False,
        "scope": "pii_read",
        "description": "Queries highly sensitive internal data bypassing normal filters.",
    },
}


def get_demo_tools() -> list:
    return list(DEMO_TOOLS_STATE.values())


def toggle_demo_tool(tool_key: str, enabled: bool) -> dict:
    """
    Enables/Disables demo tool, updates policy YAML on disk, reloads policy,
    writes audit entry, and triggers governance versioning & integrity check.
    """
    found_item = None
    for item in DEMO_TOOLS_STATE.values():
        if item["key"] == tool_key or item["name"].lower() == tool_key.lower().replace("_", " "):
            found_item = item
            break

    if not found_item:
        # Default fallback
        found_item = DEMO_TOOLS_STATE["delete_financial_report"]

    found_item["allowed"] = enabled
    agent_id = found_item["agent_id"]
    policy_path = AGENTS_DIR / agent_id / "policy.yaml"

    if policy_path.exists():
        with open(policy_path, "r", encoding="utf-8") as f:
            policy_data = yaml.safe_load(f) or {}

        allowed_tools = policy_data.get("allowed_tools", [])
        tool_exists = False

        for t in allowed_tools:
            if t.get("name") == found_item["key"]:
                t["allowed"] = enabled
                tool_exists = True
                break

        if not tool_exists:
            allowed_tools.append(
                {
                    "name": found_item["key"],
                    "scope": found_item["scope"],
                    "resource": "database",
                    "tables": ["reports"],
                    "contains_pii": False,
                    "allowed": enabled,
                }
            )

        policy_data["allowed_tools"] = allowed_tools

        with open(policy_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(policy_data, f)

    # 1. Write Audit Log Entry
    write_audit_entry(
        {
            "agent_id": agent_id,
            "event_type": "POLICY_UPDATE",
            "decision": "ALLOWED" if enabled else "DENIED",
            "reason": f"Tool '{found_item['name']}' was {'ENABLED' if enabled else 'DISABLED'} via Governance Settings.",
            "tool_name": found_item["key"],
        }
    )

    # 2. Check and Create Version
    metadata = {
        "changed_tools": [{"name": found_item["key"], "status": "enabled" if enabled else "disabled"}],
        "changed_policies": [f"{agent_id}/policy.yaml"]
    }
    check_and_create_version_on_startup(
        change_summary=f"Updated governance policy for {found_item['name']} ({'enabled' if enabled else 'disabled'})",
        metadata=metadata
    )

    # 3. Verify Integrity
    integrity = verify_system_integrity()

    return {
        "tool": found_item,
        "enabled": enabled,
        "message": f"Tool '{found_item['name']}' updated successfully.",
        "integrity": integrity,
    }


def toggle_safemode(enabled: bool) -> dict:
    set_safe_mode_override(enabled)
    integrity = verify_system_integrity()
    write_audit_entry(
        {
            "agent_id": "system",
            "event_type": "SAFE_MODE_TOGGLE",
            "decision": "ALLOWED",
            "reason": f"Safe Mode simulation set to {enabled}",
        }
    )
    return {"safe_mode": enabled, "integrity": integrity}


def run_sample() -> dict:
    return {"status": "success", "result": run_pipeline(101, auto_approve_hitl=True)}


def trigger_policy_violation() -> dict:
    return {"status": "blocked", "reason": "Policy violation simulated: scope delete denied."}


def reset_demo() -> dict:
    init_db()
    set_safe_mode_override(False)
    return {"status": "reset_complete"}


def load_sample_data() -> dict:
    init_db()
    return {"status": "sample_data_loaded"}
