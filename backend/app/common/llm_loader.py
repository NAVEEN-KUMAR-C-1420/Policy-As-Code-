"""
Shared LLM Loader
==================
This is the ONLY place in the whole project that knows how to build
an LLM object. Every agent's llm_config.py calls get_llm() from here.

It now also enforces model approval via policy before creating the LLM.

Why this matters: if you want to switch from Groq to OpenAI or
Anthropic later, you only edit config/providers.yaml. You never have
to touch this file or any agent's code.
"""

import os

import yaml

from core.paths import CONFIG_DIR
from middleware.audit_log import write_audit_entry

# Path to the shared provider config file (config/providers.yaml)
PROVIDERS_CONFIG_PATH = CONFIG_DIR / "providers.yaml"


def _load_provider_config():
    """Read config/providers.yaml and return it as a plain dictionary."""
    with open(PROVIDERS_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_llm(temperature=0.2, model_override=None, max_tokens=None, policy=None, agent_id=""):
    """
    Build and return a LangChain chat model for whichever provider
    is currently marked as "active_provider" in providers.yaml.

    Parameters:
        temperature    - creativity setting for the model (0 = strict, 1 = creative)
        model_override - optional model name from the agent's own agent.yaml
        max_tokens     - optional max tokens from agent.yaml
        policy         - optional policy dict; if provided, model is checked
                         against approved_models
        agent_id       - agent identifier for audit logging
    """
    config = _load_provider_config()
    active_provider_name = config["active_provider"]
    provider_settings = config["providers"][active_provider_name]

    model_name = model_override or provider_settings["default_model"]

    # ---- Enforce approved models if policy is provided ----
    if policy is not None:
        approved_models = policy.get("approved_models", [])
        if model_name not in approved_models:
            write_audit_entry(
                {
                    "agent_id": agent_id,
                    "event_type": "MODEL_CHECK",
                    "decision": "MODEL_DENIED",
                    "reason": (f"Model '{model_name}' is not in approved_models: " f"{approved_models}"),
                    "requested_model": model_name,
                    "approved_models": approved_models,
                }
            )
            raise ValueError(
                f"MODEL BLOCKED BY POLICY: '{model_name}' is not in "
                f"approved_models for agent '{agent_id}'. "
                f"Approved: {approved_models}"
            )

        write_audit_entry(
            {
                "agent_id": agent_id,
                "event_type": "MODEL_CHECK",
                "decision": "ALLOWED",
                "requested_model": model_name,
            }
        )

    api_key = os.environ.get(provider_settings["api_key_env"])

    if not api_key:
        raise ValueError(
            f"Missing API key for provider '{active_provider_name}'. "
            f"Please set {provider_settings['api_key_env']} in your .env file."
        )

    # Build kwargs that all providers accept
    common_kwargs = {
        "model": model_name,
        "temperature": temperature,
        "api_key": api_key,
    }
    if max_tokens is not None:
        common_kwargs["max_tokens"] = max_tokens

    # Use structural pattern matching to pick the right LangChain class.
    match active_provider_name:
        case "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(**common_kwargs)

        case "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(**common_kwargs)

        case "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(**common_kwargs)

        case _:
            raise ValueError(f"Unknown provider '{active_provider_name}' in config/providers.yaml")
