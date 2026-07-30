from core.paths import AGENTS_DIR
from pathlib import Path
import os
import yaml
import sys

from core.paths import BASE_DIR as PROJECT_ROOT
sys.path.append(PROJECT_ROOT)

from middleware.policy_validator import validate_policy
from middleware.policy_loader import load_policy

AGENTS_DIR = AGENTS_DIR

def list_policies() -> list:
    if not Path(AGENTS_DIR).exists():
        return []
    agents = [d for d in os.listdir(AGENTS_DIR) if os.path.isdir(AGENTS_DIR / d)]
    policies = []
    for agent in agents:
        policy_path = os.path.join(AGENTS_DIR, agent, "policy.yaml")
        if Path(policy_path).exists():
            policies.append(agent)
    return policies

def get_policy(agent_id: str) -> dict:
    policy_path = os.path.join(AGENTS_DIR, agent_id, "policy.yaml")
    if not Path(policy_path).exists():
        raise ValueError("Policy not found")
    return load_policy(policy_path)

def validate_policy_content(policy_yaml: str) -> dict:
    try:
        policy_dict = yaml.safe_load(policy_yaml)
        result = validate_policy(policy_dict)
        if result.valid:
            return {"status": "VALID"}
        else:
            return {"status": "INVALID", "errors": result.errors}
    except Exception as e:
        return {"status": "INVALID", "errors": [str(e)]}

def deploy_policy(agent_id: str, policy_yaml: str, commit_sha: str = None) -> dict:
    validation = validate_policy_content(policy_yaml)
    if validation["status"] != "VALID":
        raise ValueError(f"Policy is invalid: {validation.get('errors')}")
        
    policy_path = os.path.join(AGENTS_DIR, agent_id, "policy.yaml")
    with open(policy_path, "w", encoding="utf-8") as f:
        f.write(policy_yaml)
        
    from middleware.audit_log import write_audit_entry
    write_audit_entry({
        "agent_id": agent_id,
        "event_type": "POLICY_DEPLOY",
        "decision": "ALLOWED",
        "reason": f"Deployed new policy for agent {agent_id}"
    })
    
    from api.services.version_service import create_version
    version_info = create_version(agent_id, commit_sha, policy_yaml)
        
    return version_info

def reload_policy() -> dict:
    return {"status": "reloaded"}

def _recursive_diff(current: dict, historical: dict, path=""):
    diffs = {"added": {}, "removed": {}, "modified": {}}
    
    current_keys = set(current.keys()) if isinstance(current, dict) else set()
    historical_keys = set(historical.keys()) if isinstance(historical, dict) else set()
    
    for k in current_keys - historical_keys:
        diffs["added"][f"{path}.{k}".strip(".")] = current[k]
    
    for k in historical_keys - current_keys:
        diffs["removed"][f"{path}.{k}".strip(".")] = historical[k]
        
    for k in current_keys.intersection(historical_keys):
        c_val = current[k]
        h_val = historical[k]
        
        if isinstance(c_val, dict) and isinstance(h_val, dict):
            sub_diff = _recursive_diff(c_val, h_val, f"{path}.{k}".strip("."))
            diffs["added"].update(sub_diff["added"])
            diffs["removed"].update(sub_diff["removed"])
            diffs["modified"].update(sub_diff["modified"])
        elif c_val != h_val:
            diffs["modified"][f"{path}.{k}".strip(".")] = {"old": h_val, "new": c_val}
            
    return diffs

def diff_policies(agent_id: str, commit_sha: str) -> dict:
    # Get current runtime
    current_dict = get_policy(agent_id)
    
    # Get historical
    from api.services.version_service import get_historical_policy
    historical = get_historical_policy(agent_id, commit_sha)
    historical_dict = yaml.safe_load(historical["policy_yaml"])
    
    diff_result = _recursive_diff(current_dict, historical_dict)
    
    return {
        "status": "diff_completed",
        "expected_policy": "Runtime vs History",
        "differences": diff_result
    }

def get_policy_schema() -> dict:
    return {"schema": "See middleware/policy_validator.py for full schema details."}
