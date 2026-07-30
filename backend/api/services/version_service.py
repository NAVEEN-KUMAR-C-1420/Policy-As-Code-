from core.paths import AGENTS_DIR
from pathlib import Path
import os
import sys
import hashlib
import subprocess
from datetime import datetime, timezone
import glob

from core.paths import BASE_DIR as PROJECT_ROOT
sys.path.append(PROJECT_ROOT)

from common.db import run_query, run_write
from middleware.audit_log import write_audit_entry
from common.repositories import GovernanceVersionRepository, AuditRepository, GovernanceRepository

AGENTS_DIR = AGENTS_DIR
MIDDLEWARE_DIR = PROJECT_ROOT / "middleware"

# --- Backward compatibility methods (for /policies/{agent_id}/versions) ---
def create_version(agent_id: str, commit_sha: str, policy_yaml: str) -> dict:
    if not commit_sha:
        commit_sha = "local_sqlite_head"
    policy_hash = hashlib.sha256(policy_yaml.encode("utf-8")).hexdigest()
    deployed_at = datetime.now(timezone.utc).isoformat()
    run_write("UPDATE policy_versions SET is_active = 0 WHERE agent_id = ?", (agent_id,))
    run_write("""
        INSERT INTO policy_versions 
        (agent_id, commit_sha, policy_hash, policy_yaml, deployed_at, deployed_by, deployment_source, is_active, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (agent_id, commit_sha, policy_hash, policy_yaml, deployed_at, "system", "api", 1, "Deployed via API"))
    rows = run_query("SELECT version_id FROM policy_versions WHERE agent_id = ? AND commit_sha = ? ORDER BY version_id DESC LIMIT 1", (agent_id, commit_sha))
    return {"version_id": rows[0]["version_id"], "commit_sha": commit_sha, "hash": policy_hash, "timestamp": deployed_at}

def get_versions(agent_id: str) -> list:
    rows = run_query("SELECT version_id, commit_sha, policy_hash, deployed_at, is_active FROM policy_versions WHERE agent_id = ? ORDER BY deployed_at DESC", (agent_id,))
    return [dict(r) for r in rows]

def get_historical_policy(agent_id: str, commit_sha: str) -> dict:
    rows = run_query("SELECT * FROM policy_versions WHERE agent_id = ? AND commit_sha = ? ORDER BY version_id DESC LIMIT 1", (agent_id, commit_sha))
    if not rows:
        raise ValueError(f"Version {commit_sha} not found for agent {agent_id}")
    row = dict(rows[0])
    policy_yaml = row.pop("policy_yaml")
    return {"metadata": row, "policy_yaml": policy_yaml}

def rollback_policy(agent_id: str, commit_sha: str) -> dict:
    historical = get_historical_policy(agent_id, commit_sha)
    policy_yaml = historical["policy_yaml"]
    run_write("UPDATE policy_versions SET is_active = 0 WHERE agent_id = ?", (agent_id,))
    run_write("UPDATE policy_versions SET is_active = 1 WHERE version_id = ?", (historical["metadata"]["version_id"],))
    policy_path = os.path.join(AGENTS_DIR, agent_id, "policy.yaml")
    with open(policy_path, "w", encoding="utf-8") as f:
        f.write(policy_yaml)
    write_audit_entry({
        "agent_id": agent_id, "event_type": "POLICY_ROLLBACK", "decision": "ALLOWED", "reason": f"Rolled back to commit {commit_sha}"
    })
    return historical["metadata"]

# --- New Enterprise Global Governance Versioning ---

def _hash_file(filepath: str) -> str:
    if not Path(filepath).exists():
        return ""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def _hash_files_in_dir(directory: str, ext: str) -> str:
    hasher = hashlib.sha256()
    # Ensure consistent order across OSes
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if file.endswith(ext):
                filepath = root / file
                with open(filepath, "rb") as f:
                    hasher.update(f.read())
    return hasher.hexdigest()

def generate_system_hashes() -> dict:
    """Generate independent hashes for policies, agents, and governance configurations."""
    # Policy hash: all policy.yaml files in agents dir
    policy_hasher = hashlib.sha256()
    agent_hasher = hashlib.sha256()
    
    for root, _, files in os.walk(AGENTS_DIR):
        for file in sorted(files):
            filepath = root / file
            if file == "policy.yaml":
                with open(filepath, "rb") as f: policy_hasher.update(f.read())
            elif file == "agent.yaml" or file.endswith(".py"):
                with open(filepath, "rb") as f: agent_hasher.update(f.read())
                
    governance_hash = _hash_files_in_dir(MIDDLEWARE_DIR, ".py")
    
    return {
        "policy_hash": policy_hasher.hexdigest(),
        "agent_hash": agent_hasher.hexdigest(),
        "governance_hash": governance_hash
    }

def _get_git_info() -> dict:
    """Extract Git metadata safely."""
    try:
        commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, stderr=subprocess.DEVNULL).decode().strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=PROJECT_ROOT, stderr=subprocess.DEVNULL).decode().strip()
        return {"commit_sha": commit_sha, "branch": branch}
    except Exception:
        return {"commit_sha": None, "branch": None}

def check_and_create_version_on_startup():
    """Checks if the tracked files have changed since the active version, and increments a new version if so."""
    active_version = GovernanceVersionRepository.get_active_version()
    current_hashes = generate_system_hashes()
    
    # If no changes and an active version exists, do nothing.
    if active_version:
        if (active_version.get("policy_hash") == current_hashes["policy_hash"] and 
            active_version.get("agent_hash") == current_hashes["agent_hash"] and 
            active_version.get("governance_hash") == current_hashes["governance_hash"]):
            return

    latest_version = GovernanceVersionRepository.get_latest_version()
    next_version_number = (latest_version["version_number"] + 1) if latest_version else 1
    
    git_info = _get_git_info()
    
    GovernanceVersionRepository.deactivate_all()
    
    version_data = {
        "version_number": next_version_number,
        "git_commit_sha": git_info["commit_sha"],
        "git_branch": git_info["branch"],
        "policy_hash": current_hashes["policy_hash"],
        "agent_hash": current_hashes["agent_hash"],
        "governance_hash": current_hashes["governance_hash"],
        "change_summary": "System startup detected changes in governed files",
        "is_active": True,
        "rolled_back_from": None,
        "rollback_timestamp": None,
        "metadata": {"auto_generated": True}
    }
    
    GovernanceVersionRepository.create_version(version_data)
    
    AuditRepository.save({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": "system",
        "event_type": "VERSION_CREATED",
        "decision": "ALLOWED",
        "reason": f"Created new governance version {next_version_number}",
        "policy_version": str(next_version_number)
    })
    
    GovernanceRepository.log_event(
        event_type="VERSION_CREATED",
        description=f"Created new governance version {next_version_number} due to tracked file changes.",
        agent="system",
        policy_version=str(next_version_number)
    )

def rollback_global_version(version_number: int = None, commit_sha: str = None) -> dict:
    """Logical rollback. Sets the specified version as active."""
    if commit_sha:
        target_version = GovernanceVersionRepository.get_by_commit(commit_sha)
        if not target_version:
            raise ValueError(f"Version with commit {commit_sha} not found")
    elif version_number:
        target_version = GovernanceVersionRepository.get_version(version_number)
        if not target_version:
            raise ValueError(f"Version {version_number} not found")
    else:
        raise ValueError("Must provide version_number or commit_sha")
        
    current_active = GovernanceVersionRepository.get_active_version()
    old_version_number = current_active["version_number"] if current_active else None
    
    GovernanceVersionRepository.set_active_version(target_version["version_number"], rolled_back_from=old_version_number)
    
    AuditRepository.save({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": "system",
        "event_type": "VERSION_ROLLBACK",
        "decision": "ALLOWED",
        "reason": f"Rolled back to version {target_version['version_number']}",
        "policy_version": str(target_version['version_number'])
    })
    
    GovernanceRepository.log_event(
        event_type="VERSION_ROLLBACK",
        description=f"Rolled back governance version from {old_version_number} to {target_version['version_number']}.",
        agent="system",
        policy_version=str(target_version['version_number'])
    )
    
    return GovernanceVersionRepository.get_active_version()

def get_all_global_versions() -> list:
    return GovernanceVersionRepository.get_all_versions()

def get_global_active_version() -> dict:
    return GovernanceVersionRepository.get_active_version()

def get_global_version(version_number: int) -> dict:
    return GovernanceVersionRepository.get_version(version_number)
    
def get_global_version_by_commit(commit_sha: str) -> dict:
    return GovernanceVersionRepository.get_by_commit(commit_sha)
