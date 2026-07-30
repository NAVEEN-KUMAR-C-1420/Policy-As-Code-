"""
Shared LLM Loader
==================
This is the ONLY place in the whole project that knows how to build
an LLM object. Every agent's llm_config.py calls get_llm() from here.

Why this matters: if you want to switch from Groq to OpenAI or
Anthropic later, you only edit config/providers.yaml. You never have
to touch this file or any agent's code.
"""

import os
import yaml

# Path to the shared provider config file (config/providers.yaml)
PROVIDERS_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "providers.yaml"
)


def _load_provider_config():
    """Read config/providers.yaml and return it as a plain dictionary."""
    with open(PROVIDERS_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def get_llm(temperature=0.2, model_override=None):
    """
    Build and return a LangChain chat model for whichever provider
    is currently marked as "active_provider" in providers.yaml.

    Parameters:
        temperature    - creativity setting for the model (0 = strict, 1 = creative)
        model_override - optional model name from the agent's own agent.yaml
    """
    config = _load_provider_config()
    active_provider_name = config["active_provider"]
    provider_settings = config["providers"][active_provider_name]

    model_name = model_override or provider_settings["default_model"]
    api_key = os.environ.get(provider_settings["api_key_env"])

    if not api_key:
        raise ValueError(
            f"Missing API key for provider '{active_provider_name}'. "
            f"Please set {provider_settings['api_key_env']} in your .env file."
        )

    # A simple if/elif chain to pick the right LangChain class.
    # Adding a new provider later just means adding one more "elif" here
    # plus one more entry in config/providers.yaml.
    if active_provider_name == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model_name, temperature=temperature, api_key=api_key)

    elif active_provider_name == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name, temperature=temperature, api_key=api_key)

    elif active_provider_name == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model_name, temperature=temperature, api_key=api_key)

    else:
        raise ValueError(
            f"Unknown provider '{active_provider_name}' in config/providers.yaml"
        )
