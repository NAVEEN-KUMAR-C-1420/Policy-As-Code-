"""
Comprehensive Governance Test Suite
======================================
Tests all policy validation, agent/policy compatibility, tool enforcement,
rate limiting, PII/data access governance, risk calculation, HITL, and
audit logging.

ALL tests run WITHOUT external LLM API credentials.

Run with:
    python -m pytest test_governance.py -v

Or simply:
    python test_governance.py
"""

import os
import sys
import json
import copy
import tempfile
import sqlite3

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

# Make sure the dummy database exists
from data.init_db import main as init_db
init_db()

from middleware.policy_validator import (
    validate_policy,
    PolicyValidationError,
    PolicyValidationResult,
)
from middleware.agent_policy_compat import (
    validate_agent_policy_compat,
    AgentPolicyCompatError,
)
from middleware.tool_interceptor import guard_tool, reset_call_counters
from middleware.audit_log import write_audit_entry, read_recent_entries
from middleware.hitl import check_hitl
from middleware.policy_loader import load_policy


# ================================================================
# Helper: a complete valid policy for testing
# ================================================================

def _make_valid_policy():
    """Return a minimal but complete valid policy dictionary."""
    return {
        "agent_id": "test_agent",
        "policy_version": "1.0",
        "approved_models": ["openai/gpt-oss-120b"],
        "allowed_tools": [
            {
                "name": "test_tool",
                "scope": "read",
                "resource": "sqlite",
                "tables": ["transactions"],
                "contains_pii": False,
                "allowed": True,
            },
            {
                "name": "denied_tool",
                "scope": "delete",
                "resource": "sqlite",
                "tables": ["reports"],
                "contains_pii": False,
                "allowed": False,
            },
        ],
        "denied_scopes": ["delete"],
        "guardrails": {
            "pii_protection": True,
            "prompt_injection_protection": True,
            "harmful_content_filter": True,
        },
        "hitl": {
            "enabled": True,
            "risk_threshold": 0.70,
            "high_risk_requires_approval": True,
        },
        "data_access": {
            "pii_allowed": False,
            "allowed_tables": ["transactions"],
        },
        "data_retention": {
            "reports_days": 90,
            "audit_logs_days": 365,
        },
        "regulatory_frameworks": ["internal-financial-governance"],
        "rate_limits": {"max_calls_per_tool": 3},
        "audit": {
            "enabled": True,
            "log_inputs": True,
            "log_outputs": True,
            "log_denied_actions": True,
        },
    }


def _make_valid_agent_config():
    """Return a matching valid agent config."""
    return {
        "agent_id": "test_agent",
        "name": "Test Agent",
        "description": "A test agent",
        "provider": "groq",
        "model": "openai/gpt-oss-120b",
        "temperature": 0.2,
        "max_tokens": 1024,
        "tools": ["test_tool"],
    }


# ================================================================
# TEST 1: Valid policy passes validation
# ================================================================

def test_01_valid_policy_passes():
    policy = _make_valid_policy()
    result = validate_policy(policy)
    assert result.valid, f"Valid policy should pass: {result.errors}"
    print("  PASS: TEST 01 - Valid policy passes validation")


# ================================================================
# TEST 2: Policy missing approved_models fails
# ================================================================

def test_02_missing_approved_models():
    policy = _make_valid_policy()
    del policy["approved_models"]
    result = validate_policy(policy)
    assert not result.valid, "Should fail without approved_models"
    assert any("approved_models" in e for e in result.errors)
    print("  PASS: TEST 02 - Missing approved_models fails")


# ================================================================
# TEST 3: Policy missing HITL fails
# ================================================================

def test_03_missing_hitl():
    policy = _make_valid_policy()
    del policy["hitl"]
    result = validate_policy(policy)
    assert not result.valid, "Should fail without hitl"
    assert any("hitl" in e for e in result.errors)
    print("  PASS: TEST 03 - Missing HITL fails")


# ================================================================
# TEST 4: Policy missing data_retention fails
# ================================================================

def test_04_missing_retention():
    policy = _make_valid_policy()
    del policy["data_retention"]
    result = validate_policy(policy)
    assert not result.valid, "Should fail without data_retention"
    assert any("data_retention" in e for e in result.errors)
    print("  PASS: TEST 04 - Missing data_retention fails")


# ================================================================
# TEST 5: Agent ID mismatch fails
# ================================================================

def test_05_agent_id_mismatch():
    agent = _make_valid_agent_config()
    policy = _make_valid_policy()
    agent["agent_id"] = "wrong_agent"
    result = validate_agent_policy_compat(agent, policy)
    assert not result.valid, "Should fail with mismatched agent_id"
    assert any("mismatch" in e.lower() for e in result.errors)
    print("  PASS: TEST 05 - Agent ID mismatch fails")


# ================================================================
# TEST 6: Unapproved model fails
# ================================================================

def test_06_unapproved_model():
    agent = _make_valid_agent_config()
    policy = _make_valid_policy()
    agent["model"] = "dangerous/untrusted-model"
    result = validate_agent_policy_compat(agent, policy)
    assert not result.valid, "Should fail with unapproved model"
    assert any("approved_models" in e for e in result.errors)
    print("  PASS: TEST 06 - Unapproved model fails")


# ================================================================
# TEST 7: Agent declares tool absent from policy → fails
# ================================================================

def test_07_tool_not_in_policy():
    agent = _make_valid_agent_config()
    policy = _make_valid_policy()
    agent["tools"] = ["test_tool", "nonexistent_tool"]
    result = validate_agent_policy_compat(agent, policy)
    assert not result.valid, "Should fail when agent uses tool not in policy"
    assert any("nonexistent_tool" in e for e in result.errors)
    print("  PASS: TEST 07 - Agent declares tool absent from policy fails")


# ================================================================
# TEST 8: Explicit allowed tool executes
# ================================================================

def test_08_allowed_tool_executes():
    reset_call_counters()
    policy = _make_valid_policy()

    def _real_tool(x: int) -> str:
        return f"result_{x}"

    guarded = guard_tool("test_tool", policy, "test_agent", _real_tool)
    result = guarded(42)
    assert result == "result_42", f"Expected 'result_42', got '{result}'"
    print("  PASS: TEST 08 - Allowed tool executes correctly")


# ================================================================
# TEST 9: Explicit denied tool is blocked
# ================================================================

def test_09_denied_tool_blocked():
    reset_call_counters()
    policy = _make_valid_policy()

    def _dangerous(x: int) -> str:
        return "THIS SHOULD NEVER RUN"

    guarded = guard_tool("denied_tool", policy, "test_agent", _dangerous)
    result = guarded(1)
    assert "BLOCKED" in result, f"Denied tool should be blocked: {result}"
    print("  PASS: TEST 09 - Denied tool is blocked")


# ================================================================
# TEST 10: Unknown tool is blocked (default-DENY)
# ================================================================

def test_10_unknown_tool_blocked():
    reset_call_counters()
    policy = _make_valid_policy()

    def _unknown(x: int) -> str:
        return "THIS SHOULD NEVER RUN"

    guarded = guard_tool("totally_unknown_tool", policy, "test_agent", _unknown)
    result = guarded(1)
    assert "BLOCKED" in result, f"Unknown tool should be blocked: {result}"
    print("  PASS: TEST 10 - Unknown tool is blocked (default-DENY)")


# ================================================================
# TEST 11: Tool with denied scope is blocked even if allowed=true
# ================================================================

def test_11_denied_scope_overrides_allow():
    reset_call_counters()
    policy = _make_valid_policy()
    # Create a tool that says allowed=true but scope is in denied_scopes
    policy["allowed_tools"].append({
        "name": "sneaky_delete",
        "scope": "delete",
        "resource": "sqlite",
        "tables": [],
        "contains_pii": False,
        "allowed": True,  # says allowed, but scope is denied
    })

    def _sneaky(x: int) -> str:
        return "THIS SHOULD NEVER RUN"

    guarded = guard_tool("sneaky_delete", policy, "test_agent", _sneaky)
    result = guarded(1)
    assert "BLOCKED" in result, (
        f"Tool with denied scope should be blocked even if allowed=true: {result}"
    )
    print("  PASS: TEST 11 - Denied scope overrides allow (defense in depth)")


# ================================================================
# TEST 12: Rate limit is enforced
# ================================================================

def test_12_rate_limit():
    reset_call_counters()
    policy = _make_valid_policy()
    policy["rate_limits"]["max_calls_per_tool"] = 2

    def _limited(x: int) -> str:
        return f"call_{x}"

    guarded = guard_tool("test_tool", policy, "test_agent", _limited)

    r1 = guarded(1)
    assert "call_1" == r1
    r2 = guarded(2)
    assert "call_2" == r2
    r3 = guarded(3)
    assert "BLOCKED" in r3 and "rate limit" in r3.lower(), (
        f"Third call should be rate limited: {r3}"
    )
    print("  PASS: TEST 12 - Rate limit is enforced")


# ================================================================
# TEST 13: PII/table restriction is enforced
# ================================================================

def test_13_table_restriction():
    reset_call_counters()
    policy = _make_valid_policy()
    # Add a tool that accesses a table not in allowed_tables
    policy["allowed_tools"].append({
        "name": "read_accounts",
        "scope": "read",
        "resource": "sqlite",
        "tables": ["accounts"],  # but allowed_tables only has "transactions"
        "contains_pii": False,
        "allowed": True,
    })

    def _read_accts(x: int) -> str:
        return "THIS SHOULD NEVER RUN"

    guarded = guard_tool("read_accounts", policy, "test_agent", _read_accts)
    result = guarded(1)
    assert "BLOCKED" in result, f"Table restriction should block: {result}"
    assert "accounts" in result.lower()
    print("  PASS: TEST 13 - Table restriction is enforced")


def test_13b_pii_restriction():
    reset_call_counters()
    policy = _make_valid_policy()
    # Add a tool that contains PII
    policy["allowed_tools"].append({
        "name": "read_pii_data",
        "scope": "read",
        "resource": "sqlite",
        "tables": ["transactions"],
        "contains_pii": True,  # but pii_allowed=false
        "allowed": True,
    })

    def _read_pii(x: int) -> str:
        return "THIS SHOULD NEVER RUN"

    guarded = guard_tool("read_pii_data", policy, "test_agent", _read_pii)
    result = guarded(1)
    assert "BLOCKED" in result, f"PII restriction should block: {result}"
    assert "pii" in result.lower()
    print("  PASS: TEST 13b - PII restriction is enforced")


# ================================================================
# TEST 14: Risk calculation is deterministic
# ================================================================

def test_14_deterministic_risk():
    from agents.risk_analyzer_agent.dev.tools import _calculate_risk_score
    reset_call_counters()

    # Account 101: balance=52000, outflows= -1200 + -4500 = 5700
    # ratio = 5700/52000 = 0.1096
    result_str = _calculate_risk_score(101)
    result = json.loads(result_str)

    assert result["account_id"] == 101
    assert result["balance"] == 52000.0
    assert result["total_outflow"] == 5700.0
    assert abs(result["risk_score"] - 5700.0 / 52000.0) < 0.001
    assert result["risk_level"] == "Low"

    # Run again - should get identical result
    result_str2 = _calculate_risk_score(101)
    result2 = json.loads(result_str2)
    assert result["risk_score"] == result2["risk_score"], "Risk score must be deterministic"

    print("  PASS: TEST 14 - Risk calculation is deterministic")


# ================================================================
# TEST 15: High risk triggers HITL
# ================================================================

def test_15_hitl_triggered():
    policy = _make_valid_policy()
    # Test high risk
    result = check_hitl(risk_score=0.85, policy=policy, agent_id="test_agent")
    assert result["approval_required"] is True
    assert result["status"] == "PENDING_HUMAN_APPROVAL"

    # Test low risk
    result_low = check_hitl(risk_score=0.30, policy=policy, agent_id="test_agent")
    assert result_low["approval_required"] is False
    assert result_low["status"] == "APPROVED"

    # Test HITL disabled
    policy_disabled = _make_valid_policy()
    policy_disabled["hitl"]["enabled"] = False
    result_disabled = check_hitl(risk_score=0.99, policy=policy_disabled, agent_id="test_agent")
    assert result_disabled["approval_required"] is False

    print("  PASS: TEST 15 - High risk triggers HITL, low risk does not")


# ================================================================
# TEST 16: Audit log receives governance events
# ================================================================

def test_16_audit_logging():
    # Write a test entry
    write_audit_entry({
        "agent_id": "test_agent",
        "event_type": "TEST",
        "decision": "TEST_ENTRY",
        "reason": "Verifying audit log works",
    })

    entries = read_recent_entries(10)
    assert len(entries) > 0, "Should have audit entries"

    # Find our test entry
    found = any(
        e.get("event_type") == "TEST" and e.get("decision") == "TEST_ENTRY"
        for e in entries
    )
    assert found, "Test audit entry should be in recent entries"

    # Verify entries have timestamps
    assert all("timestamp" in e for e in entries), "All entries should have timestamps"

    print("  PASS: TEST 16 - Audit log receives governance events")


# ================================================================
# TEST 17: Actual agent policies validate
# ================================================================

def test_17_real_agent_policies():
    agents = [
        "data_collector_agent",
        "risk_analyzer_agent",
        "report_writer_agent",
    ]
    for agent_name in agents:
        policy_path = os.path.join(
            PROJECT_ROOT, "agents", agent_name, "policy.yaml"
        )
        policy = load_policy(policy_path)
        result = validate_policy(policy)
        assert result.valid, (
            f"Policy for {agent_name} should be valid: {result.errors}"
        )
    print("  PASS: TEST 17 - All 3 real agent policies validate successfully")


# ================================================================
# TEST 18: Real agent/policy compatibility
# ================================================================

def test_18_real_agent_compat():
    import yaml
    agents = [
        "data_collector_agent",
        "risk_analyzer_agent",
        "report_writer_agent",
    ]
    for agent_name in agents:
        agent_dir = os.path.join(PROJECT_ROOT, "agents", agent_name)
        agent_yaml = os.path.join(agent_dir, "agent.yaml")
        policy_yaml = os.path.join(agent_dir, "policy.yaml")

        with open(agent_yaml, "r", encoding="utf-8") as f:
            agent_config = yaml.safe_load(f)
        policy = load_policy(policy_yaml)

        result = validate_agent_policy_compat(agent_config, policy)
        assert result.valid, (
            f"Agent/policy compat for {agent_name} should pass: {result.errors}"
        )
    print("  PASS: TEST 18 - All 3 real agents are compatible with their policies")


# ================================================================
# TEST 19: Delete old reports is blocked (defense in depth)
# ================================================================

def test_19_delete_blocked():
    reset_call_counters()
    from agents.report_writer_agent.dev.tools import guarded_delete_old_reports
    result = guarded_delete_old_reports(account_id=101)
    assert "BLOCKED" in result, f"delete_old_reports should be BLOCKED: {result}"
    print("  PASS: TEST 19 - delete_old_reports is blocked (defense in depth)")


# ================================================================
# TEST 20: Policy validator catches HITL threshold out of range
# ================================================================

def test_20_hitl_threshold_range():
    policy = _make_valid_policy()
    policy["hitl"]["risk_threshold"] = 1.5  # out of range
    result = validate_policy(policy)
    assert not result.valid
    assert any("risk_threshold" in e for e in result.errors)
    print("  PASS: TEST 20 - HITL threshold out of range is caught")


# ================================================================
# TEST 21: Negative retention days rejected
# ================================================================

def test_21_negative_retention():
    policy = _make_valid_policy()
    policy["data_retention"]["reports_days"] = -10
    result = validate_policy(policy)
    assert not result.valid
    assert any("reports_days" in e for e in result.errors)
    print("  PASS: TEST 21 - Negative retention days rejected")


# ================================================================
# TEST 22: Data retention functions work
# ================================================================

def test_22_data_retention():
    from middleware.data_retention import find_expired_reports
    from common.db import PROVIDER
    if PROVIDER == "supabase":
        print("  SKIP: TEST 22 - Data retention functions (SQLite only)")
        return
        
    db_path = os.path.join(PROJECT_ROOT, "data", "finance.db")
    # With retention of 9999 days, nothing should be expired
    expired = find_expired_reports(db_path, retention_days=9999)
    assert isinstance(expired, list)
    print("  PASS: TEST 22 - Data retention functions work correctly")


# ================================================================
# TEST 23: Missing regulatory_frameworks fails
# ================================================================

def test_23_missing_regulatory():
    policy = _make_valid_policy()
    del policy["regulatory_frameworks"]
    result = validate_policy(policy)
    assert not result.valid
    assert any("regulatory_frameworks" in e for e in result.errors)
    print("  PASS: TEST 23 - Missing regulatory_frameworks fails")


# ================================================================
# TEST 24: Database integrity
# ================================================================

def test_24_db_integrity():
    from common.db import PROVIDER
    if PROVIDER == "supabase":
        print("  SKIP: TEST 24 - Database integrity verified (SQLite only)")
        return
        
    db_path = os.path.join(PROJECT_ROOT, "data", "finance.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()
    assert result[0] == "ok", f"Database integrity check failed: {result}"

    # Verify tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    for expected in ["accounts", "transactions", "reports"]:
        assert expected in tables, f"Table '{expected}' missing from database"

    # Verify sample data
    cursor.execute("SELECT COUNT(*) FROM accounts")
    assert cursor.fetchone()[0] >= 3, "Should have at least 3 accounts"

    cursor.execute("SELECT COUNT(*) FROM transactions")
    assert cursor.fetchone()[0] >= 7, "Should have at least 7 transactions"

    conn.close()
    print("  PASS: TEST 24 - Database integrity verified")


