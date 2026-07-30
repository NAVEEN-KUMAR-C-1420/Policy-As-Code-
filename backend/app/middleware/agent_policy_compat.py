"""
Agent-Policy Compatibility Validator
======================================
Validates that an agent's configuration (agent.yaml) is compatible
with its governance policy (policy.yaml) BEFORE the agent starts.

Checks performed:
  1. agent_id match between agent.yaml and policy.yaml
  2. requested model is in policy.approved_models
  3. every tool declared by agent has a corresponding policy rule
  4. no agent tool is in a denied scope

This module is reusable by future CI/CD pipelines.

Usage:
    from middleware.agent_policy_compat import validate_agent_policy_compat
    result = validate_agent_policy_compat(agent_config, policy)
"""

import os
from pathlib import Path

import yaml


class AgentPolicyCompatError(Exception):
    """Raised when agent configuration is incompatible with its policy."""

    def __init__(self, errors: list):
        self.errors = errors
        super().__init__("Agent/Policy compatibility check failed:\n" + "\n".join(f"  - {e}" for e in errors))


class CompatResult:
    """Holds the result of an agent-policy compatibility check."""

    def __init__(self, valid: bool, errors: list):
        self.valid = valid
        self.errors = errors

    def __repr__(self):
        if self.valid:
            return "CompatResult(valid=True)"
        return f"CompatResult(valid=False, errors={self.errors})"


def validate_agent_policy_compat(agent_config: dict, policy: dict, raise_on_error: bool = False) -> CompatResult:
    """
    Validate that agent_config is compatible with policy.

    Parameters:
        agent_config    - parsed agent.yaml dictionary
        policy          - parsed policy.yaml dictionary
        raise_on_error  - if True, raise AgentPolicyCompatError on failure

    Returns:
        CompatResult with .valid and .errors
    """
    errors = []

    # ---- Check 1: agent_id must match ----
    agent_id = agent_config.get("agent_id", "")
    policy_id = policy.get("agent_id", "")
    if agent_id != policy_id:
        errors.append(f"Agent ID mismatch: agent.yaml has '{agent_id}' " f"but policy.yaml has '{policy_id}'")

    # ---- Check 2: model must be in approved_models ----
    requested_model = agent_config.get("model", "")
    approved_models = policy.get("approved_models", [])
    if requested_model and requested_model not in approved_models:
        errors.append(f"Model '{requested_model}' is not in policy approved_models: " f"{approved_models}")

    # ---- Check 3: every agent tool must have a policy rule ----
    agent_tools = agent_config.get("tools", [])
    policy_tools = {
        rule["name"]: rule for rule in policy.get("allowed_tools", []) if isinstance(rule, dict) and "name" in rule
    }
    denied_scopes = policy.get("denied_scopes", [])

    for tool_name in agent_tools:
        if tool_name not in policy_tools:
            errors.append(
                f"Tool '{tool_name}' is declared in agent.yaml but has "
                f"no corresponding rule in policy.yaml (default: DENY)"
            )
        else:
            rule = policy_tools[tool_name]
            # Check that the tool is actually allowed
            if not rule.get("allowed", False):
                errors.append(f"Tool '{tool_name}' is declared in agent.yaml but " f"policy.yaml sets allowed=false")
            # Check that the tool's scope is not in denied_scopes
            tool_scope = rule.get("scope", "")
            if tool_scope in denied_scopes:
                errors.append(
                    f"Tool '{tool_name}' has scope '{tool_scope}' which " f"is in denied_scopes: {denied_scopes}"
                )

    result = CompatResult(valid=len(errors) == 0, errors=errors)
    if raise_on_error and not result.valid:
        raise AgentPolicyCompatError(errors)
    return result


def load_and_validate_agent(agent_dir: str, raise_on_error: bool = True):
    """
    Convenience function: load agent.yaml and policy.yaml from an agent
    directory, validate the policy, and check compatibility.

    Parameters:
        agent_dir       - path to the agent's root directory
                          (e.g., agents/data_collector_agent/)
        raise_on_error  - if True, raise on any validation failure

    Returns:
        tuple of (agent_config, policy) if valid
    """
    from middleware.policy_validator import validate_policy

    agent_dir_path = Path(agent_dir)
    agent_yaml_path = agent_dir_path / "agent.yaml"
    policy_yaml_path = agent_dir_path / "policy.yaml"

    with open(agent_yaml_path, "r", encoding="utf-8") as f:
        agent_config = yaml.safe_load(f)

    with open(policy_yaml_path, "r", encoding="utf-8") as f:
        policy = yaml.safe_load(f)

    # Step 1: Validate the policy schema itself
    policy_result = validate_policy(policy, raise_on_error=raise_on_error)
    if not policy_result.valid:
        return None

    # Step 2: Validate agent/policy compatibility
    compat_result = validate_agent_policy_compat(agent_config, policy, raise_on_error=raise_on_error)
    if not compat_result.valid:
        return None

    return agent_config, policy
