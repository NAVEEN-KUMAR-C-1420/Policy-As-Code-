import os
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(PROJECT_ROOT, "agents")

def list_agents() -> list:
    if not os.path.exists(AGENTS_DIR):
        return []
    return [d for d in os.listdir(AGENTS_DIR) if os.path.isdir(os.path.join(AGENTS_DIR, d))]

def get_agent_details(agent_id: str) -> dict:
    config = get_agent_config(agent_id)
    return {
        "agent_id": agent_id,
        "name": config.get("name"),
        "description": config.get("description")
    }

def get_agent_status(agent_id: str) -> dict:
    yaml_path = os.path.join(AGENTS_DIR, agent_id, "agent.yaml")
    return {
        "agent_id": agent_id,
        "readiness": "ready" if os.path.exists(yaml_path) else "not_found"
    }

def get_agent_tools(agent_id: str) -> list:
    config = get_agent_config(agent_id)
    return config.get("tools", [])

def get_agent_policy(agent_id: str) -> dict:
    from middleware.policy_loader import load_policy
    policy_path = os.path.join(AGENTS_DIR, agent_id, "policy.yaml")
    if not os.path.exists(policy_path):
        raise ValueError(f"Policy not found for agent {agent_id}")
    return load_policy(policy_path)

def get_agent_config(agent_id: str) -> dict:
    agent_yaml = os.path.join(AGENTS_DIR, agent_id, "agent.yaml")
    if not os.path.exists(agent_yaml):
        raise ValueError(f"Agent config not found for agent {agent_id}")
    with open(agent_yaml, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def reload_agent_config(agent_id: str) -> dict:
    return get_agent_config(agent_id)
