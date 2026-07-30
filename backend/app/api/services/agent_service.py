import os
from pathlib import Path

import yaml

from core.paths import AGENTS_DIR
from core.paths import BASE_DIR as PROJECT_ROOT

AGENTS_DIR = AGENTS_DIR


def list_agents() -> list:
    if not AGENTS_DIR.exists():
        return []
    return [d for d in os.listdir(AGENTS_DIR) if (AGENTS_DIR / d).is_dir()]


def get_agent_details(agent_id: str) -> dict:
    config = get_agent_config(agent_id)
    return {"agent_id": agent_id, "name": config.get("name"), "description": config.get("description")}


def get_agent_status(agent_id: str) -> dict:
    yaml_path = AGENTS_DIR / agent_id / "agent.yaml"
    return {"agent_id": agent_id, "readiness": "ready" if yaml_path.exists() else "not_found"}


def get_agent_tools(agent_id: str) -> list:
    config = get_agent_config(agent_id)
    return config.get("tools", [])


def get_agent_policy(agent_id: str) -> dict:
    from middleware.policy_loader import load_policy

    policy_path = AGENTS_DIR / agent_id / "policy.yaml"
    if not policy_path.exists():
        raise ValueError(f"Policy not found for agent {agent_id}")
    return load_policy(policy_path)


def get_agent_config(agent_id: str) -> dict:
    agent_yaml = AGENTS_DIR / agent_id / "agent.yaml"
    if not agent_yaml.exists():
        raise ValueError(f"Agent config not found for agent {agent_id}")
    with open(agent_yaml, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def reload_agent_config(agent_id: str) -> dict:
    return get_agent_config(agent_id)
