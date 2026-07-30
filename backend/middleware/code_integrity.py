"""
Code Integrity & Safe Mode Engine
=================================
Computes runtime SHA256 hashes of agent code, agent configs, and policy YAMLs.
Compares runtime hashes against the active governance version in the database.

If a file has been tampered with or modified without creating a new governance version:
  - System enters SAFE MODE
  - Pipeline execution is BLOCKED
  - Governance event & Audit log entry are created
  - Frontend displays Integrity Failed alert with detailed diagnostic information.
"""

import hashlib
import os
import sys
from pathlib import Path
from typing import Any

from common.repositories import AuditRepository, GovernanceRepository, GovernanceVersionRepository
from core.paths import AGENTS_DIR, MIDDLEWARE_DIR
from core.paths import BASE_DIR as PROJECT_ROOT

_SAFE_MODE_OVERRIDE = False


def set_safe_mode_override(enabled: bool):
    """Allows manual simulation of Safe Mode via Demo/Settings endpoint."""
    global _SAFE_MODE_OVERRIDE
    _SAFE_MODE_OVERRIDE = enabled


def compute_runtime_integrity_hashes() -> dict[str, str]:
    """Generates SHA256 hashes for all governed system files."""
    policy_hasher = hashlib.sha256()
    agent_hasher = hashlib.sha256()
    governance_hasher = hashlib.sha256()

    # Hash agent policy.yaml, agent.yaml, and python tools/agents
    if AGENTS_DIR.exists():
        for root, _, files in os.walk(AGENTS_DIR):
            for file in sorted(files):
                filepath = Path(root) / file
                if file == "policy.yaml":
                    with open(filepath, "rb") as f:
                        policy_hasher.update(f.read())
                elif file == "agent.yaml" or file.endswith(".py"):
                    with open(filepath, "rb") as f:
                        agent_hasher.update(f.read())

    # Hash middleware governance files
    if MIDDLEWARE_DIR.exists():
        for root, _, files in os.walk(MIDDLEWARE_DIR):
            for file in sorted(files):
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    with open(filepath, "rb") as f:
                        governance_hasher.update(f.read())

    return {
        "policy_hash": policy_hasher.hexdigest(),
        "agent_hash": agent_hasher.hexdigest(),
        "governance_hash": governance_hasher.hexdigest(),
    }


def verify_system_integrity() -> dict[str, Any]:
    """
    Verifies runtime hashes against active version in DB.
    Returns integrity status dict.
    """
    global _SAFE_MODE_OVERRIDE

    runtime_hashes = compute_runtime_integrity_hashes()
    active_version = GovernanceVersionRepository.get_active_version()
    git_commit = "head"

    try:
        import subprocess

        git_commit = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], cwd=str(PROJECT_ROOT), stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
    except Exception:
        pass

    if _SAFE_MODE_OVERRIDE:
        return {
            "status": "FAILED",
            "safe_mode": True,
            "reason": "Safe Mode manually simulated via Developer Settings for demonstration.",
            "policy_hash": runtime_hashes["policy_hash"],
            "agent_hash": runtime_hashes["agent_hash"],
            "governance_hash": runtime_hashes["governance_hash"],
            "expected_hash": "SIMULATED_MISMATCH_HASH",
            "commit_sha": git_commit,
            "deployment_version": active_version.get("version_number", 1) if active_version else 1,
            "required_action": "Disable Safe Mode simulation in Developer Settings or create a new governance version.",
        }

    if not active_version:
        # No version record yet - system is initial state
        return {
            "status": "PASSED",
            "safe_mode": False,
            "reason": "System initialized cleanly.",
            "policy_hash": runtime_hashes["policy_hash"],
            "agent_hash": runtime_hashes["agent_hash"],
            "governance_hash": runtime_hashes["governance_hash"],
            "commit_sha": git_commit,
            "deployment_version": 1,
            "required_action": "None",
        }

    mismatches = []
    if active_version.get("policy_hash") and active_version["policy_hash"] != runtime_hashes["policy_hash"]:
        mismatches.append("policy.yaml files modified without version bump")
    if active_version.get("agent_hash") and active_version["agent_hash"] != runtime_hashes["agent_hash"]:
        mismatches.append("agent code or agent.yaml modified without version bump")
    if active_version.get("governance_hash") and active_version["governance_hash"] != runtime_hashes["governance_hash"]:
        mismatches.append("governance middleware modified without version bump")

    if mismatches:
        reason_str = "; ".join(mismatches)
        return {
            "status": "FAILED",
            "safe_mode": True,
            "reason": f"Integrity check failed: {reason_str}",
            "policy_hash": runtime_hashes["policy_hash"],
            "agent_hash": runtime_hashes["agent_hash"],
            "governance_hash": runtime_hashes["governance_hash"],
            "expected_policy_hash": active_version.get("policy_hash"),
            "expected_agent_hash": active_version.get("agent_hash"),
            "expected_governance_hash": active_version.get("governance_hash"),
            "commit_sha": git_commit,
            "deployment_version": active_version.get("version_number"),
            "required_action": "Create a new Governance Version via API/CLI or revert uncommitted code changes.",
        }

    return {
        "status": "PASSED",
        "safe_mode": False,
        "reason": "All runtime SHA256 hashes match active governance version.",
        "policy_hash": runtime_hashes["policy_hash"],
        "agent_hash": runtime_hashes["agent_hash"],
        "governance_hash": runtime_hashes["governance_hash"],
        "commit_sha": git_commit,
        "deployment_version": active_version.get("version_number", 1),
        "required_action": "None",
    }
