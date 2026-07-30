"""
LLM Configuration - Report Writer Agent
==========================================
Reads settings from ../agent.yaml and ../policy.yaml, validates
compatibility, and asks the shared llm_loader to build the LangChain
chat model with policy-enforced model approval.
"""

import os
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from common.llm_loader import get_llm
from middleware.agent_policy_compat import validate_agent_policy_compat
from middleware.policy_loader import load_policy

AGENT_DIR = Path(__file__).resolve().parent.parent
AGENT_YAML_PATH = AGENT_DIR / "agent.yaml"
POLICY_YAML_PATH = AGENT_DIR / "policy.yaml"


def load_agent_config():
    with open(AGENT_YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_agent_llm():
    config = load_agent_config()
    policy = load_policy(POLICY_YAML_PATH)

    # Validate agent/policy compatibility at startup
    validate_agent_policy_compat(config, policy, raise_on_error=True)

    return get_llm(
        temperature=config.get("temperature", 0.3),
        model_override=config.get("model"),
        max_tokens=config.get("max_tokens"),
        policy=policy,
        agent_id=config.get("agent_id", ""),
    )
