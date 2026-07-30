"""
Policy Validator
=================
Validates that a policy dictionary (loaded from policy.yaml) conforms
to the required governance schema.

This module is designed to be REUSABLE by:
  - runtime startup validation
  - agent/policy compatibility checks
  - future CI/CD pipelines

It does NOT depend on GitHub Actions, Docker, or any deployment tooling.

Usage:
    from middleware.policy_validator import validate_policy, PolicyValidationError
    result = validate_policy(policy_dict)
    # result is a PolicyValidationResult with .valid and .errors
"""


class PolicyValidationError(Exception):
    """Raised when a policy fails validation."""
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(
            "Policy validation failed:\n" +
            "\n".join(f"  - {e}" for e in errors)
        )


class PolicyValidationResult:
    """Holds the result of a policy validation."""
    def __init__(self, valid: bool, errors: list):
        self.valid = valid
        self.errors = errors

    def __repr__(self):
        if self.valid:
            return "PolicyValidationResult(valid=True)"
        return (
            f"PolicyValidationResult(valid=False, "
            f"errors={self.errors})"
        )


def validate_policy(policy: dict, raise_on_error: bool = False) -> PolicyValidationResult:
    """
    Validate a policy dictionary against the required governance schema.

    Parameters:
        policy          - the parsed policy.yaml as a dictionary
        raise_on_error  - if True, raise PolicyValidationError on failure

    Returns:
        PolicyValidationResult with .valid (bool) and .errors (list[str])
    """
    errors = []

    if not isinstance(policy, dict):
        errors.append("Policy must be a dictionary, got: " + type(policy).__name__)
        return _finish(errors, raise_on_error)

    # ---- Required top-level fields ----
    _require_string(policy, "agent_id", errors)
    _require_string(policy, "policy_version", errors)

    # ---- approved_models ----
    if "approved_models" not in policy:
        errors.append("Missing required field: 'approved_models'")
    else:
        models = policy["approved_models"]
        if not isinstance(models, list) or len(models) == 0:
            errors.append("'approved_models' must be a non-empty list of model names")
        else:
            for i, m in enumerate(models):
                if not isinstance(m, str) or not m.strip():
                    errors.append(f"'approved_models[{i}]' must be a non-empty string")

    # ---- allowed_tools ----
    if "allowed_tools" not in policy:
        errors.append("Missing required field: 'allowed_tools'")
    else:
        tools = policy["allowed_tools"]
        if not isinstance(tools, list):
            errors.append("'allowed_tools' must be a list")
        else:
            for i, tool in enumerate(tools):
                prefix = f"allowed_tools[{i}]"
                if not isinstance(tool, dict):
                    errors.append(f"'{prefix}' must be a dictionary")
                    continue
                if "name" not in tool or not isinstance(tool["name"], str):
                    errors.append(f"'{prefix}' missing or invalid 'name' (must be a string)")
                if "scope" not in tool or not isinstance(tool["scope"], str):
                    errors.append(f"'{prefix}' missing or invalid 'scope' (must be a string)")
                if "allowed" not in tool or not isinstance(tool["allowed"], bool):
                    errors.append(f"'{prefix}' missing or invalid 'allowed' (must be a boolean)")

    # ---- guardrails ----
    if "guardrails" not in policy:
        errors.append("Missing required field: 'guardrails'")
    else:
        guardrails = policy["guardrails"]
        if not isinstance(guardrails, dict):
            errors.append("'guardrails' must be a dictionary")

    # ---- hitl ----
    if "hitl" not in policy:
        errors.append("Missing required field: 'hitl'")
    else:
        hitl = policy["hitl"]
        if not isinstance(hitl, dict):
            errors.append("'hitl' must be a dictionary")
        else:
            if "enabled" not in hitl or not isinstance(hitl["enabled"], bool):
                errors.append("'hitl.enabled' must be a boolean")
            if "risk_threshold" in hitl:
                threshold = hitl["risk_threshold"]
                if not isinstance(threshold, (int, float)):
                    errors.append("'hitl.risk_threshold' must be a number")
                elif not (0.0 <= threshold <= 1.0):
                    errors.append(
                        f"'hitl.risk_threshold' must be between 0.0 and 1.0, got {threshold}"
                    )

    # ---- data_retention ----
    if "data_retention" not in policy:
        errors.append("Missing required field: 'data_retention'")
    else:
        retention = policy["data_retention"]
        if not isinstance(retention, dict):
            errors.append("'data_retention' must be a dictionary")
        else:
            for key in ["reports_days", "audit_logs_days"]:
                if key in retention:
                    val = retention[key]
                    if not isinstance(val, (int, float)) or val < 0:
                        errors.append(
                            f"'data_retention.{key}' must be a non-negative number, got {val}"
                        )

    # ---- regulatory_frameworks ----
    if "regulatory_frameworks" not in policy:
        errors.append("Missing required field: 'regulatory_frameworks'")
    else:
        frameworks = policy["regulatory_frameworks"]
        if not isinstance(frameworks, list) or len(frameworks) == 0:
            errors.append("'regulatory_frameworks' must be a non-empty list of strings")
        else:
            for i, fw in enumerate(frameworks):
                if not isinstance(fw, str) or not fw.strip():
                    errors.append(f"'regulatory_frameworks[{i}]' must be a non-empty string")

    # ---- rate_limits (optional but validated if present) ----
    if "rate_limits" in policy:
        rl = policy["rate_limits"]
        if not isinstance(rl, dict):
            errors.append("'rate_limits' must be a dictionary")
        else:
            if "max_calls_per_tool" in rl:
                val = rl["max_calls_per_tool"]
                if not isinstance(val, int) or val <= 0:
                    errors.append(
                        f"'rate_limits.max_calls_per_tool' must be a positive integer, got {val}"
                    )

    # ---- audit (optional but validated if present) ----
    if "audit" in policy:
        audit = policy["audit"]
        if not isinstance(audit, dict):
            errors.append("'audit' must be a dictionary")

    # ---- denied_scopes (optional but validated if present) ----
    if "denied_scopes" in policy:
        ds = policy["denied_scopes"]
        if not isinstance(ds, list):
            errors.append("'denied_scopes' must be a list")

    # ---- data_access (optional but validated if present) ----
    if "data_access" in policy:
        da = policy["data_access"]
        if not isinstance(da, dict):
            errors.append("'data_access' must be a dictionary")

    return _finish(errors, raise_on_error)


def _require_string(d: dict, key: str, errors: list):
    """Check that d[key] exists and is a non-empty string."""
    if key not in d:
        errors.append(f"Missing required field: '{key}'")
    elif not isinstance(d[key], str) or not d[key].strip():
        errors.append(f"'{key}' must be a non-empty string")


def _finish(errors: list, raise_on_error: bool) -> PolicyValidationResult:
    """Return a result or raise if requested."""
    result = PolicyValidationResult(valid=len(errors) == 0, errors=errors)
    if raise_on_error and not result.valid:
        raise PolicyValidationError(errors)
    return result
