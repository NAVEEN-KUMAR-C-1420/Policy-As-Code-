"""
LLM Configuration - Report Writer Agent
==========================================
Reads settings from ../agent.yaml and asks the shared llm_loader
(common/llm_loader.py) to actually build the LangChain chat model.
"""

import os
import sys
import yaml

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(PROJECT_ROOT)

from common.llm_loader import get_llm

AGENT_YAML_PATH = os.path.join(os.path.dirname(__file__), "..", "agent.yaml")


def load_agent_config():
    with open(AGENT_YAML_PATH, "r") as f:
        return yaml.safe_load(f)


def get_agent_llm():
    config = load_agent_config()
    return get_llm(
        temperature=config.get("temperature", 0.3),
        model_override=config.get("model"),
    )
