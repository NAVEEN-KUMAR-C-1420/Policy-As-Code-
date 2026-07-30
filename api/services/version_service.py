import os
import sys
import hashlib
from datetime import datetime, timezone

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from common.db import run_query, run_write
from middleware.audit_log import write_audit_entry

AGENTS_DIR = os.path.join(PROJECT_ROOT, "agents")

def create_version(agent_id: str, commit_sha: str, policy_yaml: str) -> dict:
    if not commit_sha:
        commit_sha = "local_sqlite_head"
        
    policy_hash = hashlib.sha256(policy_yaml.encode("utf-8")).hexdigest()
    deployed_at = datetime.now(timezone.utc).isoformat()
    
    # Deactivate current versions
    run_write("UPDATE policy_versions SET is_active = 0 WHERE agent_id = ?", (agent_id,))
    
    # Insert new version
    run_write("""
        INSERT INTO policy_versions 
        (agent_id, commit_sha, policy_hash, policy_yaml, deployed_at, deployed_by, deployment_source, is_active, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (agent_id, commit_sha, policy_hash, policy_yaml, deployed_at, "system", "api", 1, "Deployed via API"))
    
    # Get the inserted version
    rows = run_query("SELECT version_id FROM policy_versions WHERE agent_id = ? AND commit_sha = ? ORDER BY version_id DESC LIMIT 1", (agent_id, commit_sha))
    
    return {
        "version_id": rows[0]["version_id"],
        "commit_sha": commit_sha,
        "hash": policy_hash,
        "timestamp": deployed_at
    }

def get_versions(agent_id: str) -> list:
    rows = run_query("""
        SELECT version_id, commit_sha, policy_hash, deployed_at, is_active 
        FROM policy_versions 
        WHERE agent_id = ? 
        ORDER BY deployed_at DESC
    """, (agent_id,))
    return [dict(r) for r in rows]

def get_historical_policy(agent_id: str, commit_sha: str) -> dict:
    rows = run_query("SELECT * FROM policy_versions WHERE agent_id = ? AND commit_sha = ? ORDER BY version_id DESC LIMIT 1", (agent_id, commit_sha))
    if not rows:
        raise ValueError(f"Version {commit_sha} not found for agent {agent_id}")
    row = dict(rows[0])
    policy_yaml = row.pop("policy_yaml")
    return {
        "metadata": row,
        "policy_yaml": policy_yaml
    }

def rollback_policy(agent_id: str, commit_sha: str) -> dict:
    historical = get_historical_policy(agent_id, commit_sha)
    policy_yaml = historical["policy_yaml"]
    
    # Deactivate current versions
    run_write("UPDATE policy_versions SET is_active = 0 WHERE agent_id = ?", (agent_id,))
    
    # Reactivate the selected version
    run_write("UPDATE policy_versions SET is_active = 1 WHERE version_id = ?", (historical["metadata"]["version_id"],))
    
    # Write back to filesystem so runtime loads it
    policy_path = os.path.join(AGENTS_DIR, agent_id, "policy.yaml")
    with open(policy_path, "w", encoding="utf-8") as f:
        f.write(policy_yaml)
        
    write_audit_entry({
        "agent_id": agent_id,
        "event_type": "POLICY_ROLLBACK",
        "decision": "ALLOWED",
        "reason": f"Rolled back to commit {commit_sha}"
    })
    
    return historical["metadata"]
