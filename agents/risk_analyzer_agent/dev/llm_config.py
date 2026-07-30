"""
LLM Configuration - Risk Analyzer Agent
==========================================
Reads settings from ../agent.yaml and ../policy.yaml, validates
compatibility, and asks the shared llm_loader to build the LangChain
chat model with policy-enforced model approval.
"""

import os
import sys
import yaml

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(PROJECT_ROOT)

from common.llm_loader import get_llm
from middleware.policy_loader import load_policy
from middleware.agent_policy_compat import validate_agent_policy_compat

AGENT_DIR = os.path.join(os.path.dirname(__file__), "..")
AGENT_YAML_PATH = os.path.join(AGENT_DIR, "agent.yaml")
POLICY_YAML_PATH = os.path.join(AGENT_DIR, "policy.yaml")


def load_agent_config():
    with open(AGENT_YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_agent_llm():
    config = load_agent_config()
    policy = load_policy(POLICY_YAML_PATH)

    # Validate agent/policy compatibility at startup
    validate_agent_policy_compat(config, policy, raise_on_error=True)

    return get_llm(
        temperature=config.get("temperature", 0.2),
        model_override=config.get("model"),
        max_tokens=config.get("max_tokens"),
        policy=policy,
        agent_id=config.get("agent_id", ""),
    )
