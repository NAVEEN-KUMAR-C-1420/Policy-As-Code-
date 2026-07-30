"""
Tool Interception Middleware
==============================
This is the heart of the AI governance layer.

Every single tool in this project is wrapped with guard_tool() before
it is handed to a LangChain agent. That means NO tool call ever runs
directly - it always passes through this checkpoint first, which:

  1. Looks up the tool's rule in the agent's policy.yaml
  2. Blocks the call if the tool is not explicitly allowed
  3. Blocks the call if the tool's scope is in denied_scopes
  4. Enforces data access / table / PII restrictions
  5. Blocks the call if the agent has exceeded its rate limit
  6. Runs the real tool only if ALL checks pass
  7. Writes an audit log entry for every decision

Deny rules ALWAYS take precedence over allow rules.
Unknown tools default to DENY.
"""

import functools

from middleware.audit_log import write_audit_entry

# Keeps track of how many times each (agent, tool) pair has been called
# during this process, so we can enforce simple rate limits.
_call_counters = {}


def reset_call_counters():
    """Reset all rate-limit counters. Useful for testing."""
    global _call_counters
    _call_counters = {}


def _find_tool_rule(policy: dict, tool_name: str):
    """Look up the policy rule for one specific tool name."""
    for rule in policy.get("allowed_tools", []):
        if rule.get("name") == tool_name:
            return rule
    return None


def guard_tool(tool_name: str, policy: dict, agent_id: str, original_function):
    """
    Wrap a plain python function (the real tool logic) with policy
    enforcement and audit logging.

    Parameters:
        tool_name         - the name this tool is registered under in policy.yaml
        policy            - the loaded policy.yaml dictionary for this agent
        agent_id          - the id of the agent that owns this tool
        original_function - the real function that does the actual work

    Returns a new function with the exact same signature as
    original_function (thanks to functools.wraps), so LangChain can
    still automatically detect its parameters.
    """

    @functools.wraps(original_function)
    def wrapped_function(*args, **kwargs):
        rule = _find_tool_rule(policy, tool_name)
        denied_scopes = policy.get("denied_scopes", [])
        audit_config = policy.get("audit", {})
        log_inputs = audit_config.get("log_inputs", True)
        log_outputs = audit_config.get("log_outputs", True)

        # Build safe argument representation for audit
        safe_args = str(args) if log_inputs else "[redacted]"
        safe_kwargs = str(kwargs) if log_inputs else "[redacted]"

        counter_key = f"{agent_id}:{tool_name}"

        # ---- Check 1: is this tool known at all? (default-DENY) ----
        if rule is None:
            write_audit_entry({
                "agent_id": agent_id,
                "event_type": "TOOL_CALL",
                "tool_name": tool_name,
                "scope": "unknown",
                "args": safe_args,
                "kwargs": safe_kwargs,
                "decision": "DENIED",
                "reason": "Tool not found in policy (default: DENY)",
            })
            return (
                f"BLOCKED BY POLICY: agent '{agent_id}' is not allowed "
                f"to use tool '{tool_name}' (unknown tool)."
            )

        tool_scope = rule.get("scope", "")

        # ---- Check 2: is the tool explicitly disallowed? ----
        if rule.get("allowed") is not True:
            write_audit_entry({
                "agent_id": agent_id,
                "event_type": "TOOL_CALL",
                "tool_name": tool_name,
                "scope": tool_scope,
                "args": safe_args,
                "kwargs": safe_kwargs,
                "decision": "DENIED",
                "reason": "Tool is set to allowed=false in policy",
            })
            return (
                f"BLOCKED BY POLICY: agent '{agent_id}' is not allowed "
                f"to use tool '{tool_name}'."
            )

        # ---- Check 3: is the tool's scope in denied_scopes? ----
        # Deny rules take precedence over allow rules
        if tool_scope in denied_scopes:
            write_audit_entry({
                "agent_id": agent_id,
                "event_type": "TOOL_CALL",
                "tool_name": tool_name,
                "scope": tool_scope,
                "args": safe_args,
                "kwargs": safe_kwargs,
                "decision": "DENIED",
                "reason": (
                    f"Tool scope '{tool_scope}' is in denied_scopes "
                    f"{denied_scopes} (deny takes precedence over allow)"
                ),
            })
            return (
                f"BLOCKED BY POLICY: agent '{agent_id}' cannot use "
                f"tool '{tool_name}' because scope '{tool_scope}' is denied."
            )

        # ---- Check 4: data access / table restrictions ----
        data_access = policy.get("data_access", {})
        allowed_tables = data_access.get("allowed_tables", None)
        pii_allowed = data_access.get("pii_allowed", True)

        # Check table access
        tool_tables = rule.get("tables", [])
        if allowed_tables is not None and tool_tables:
            for table in tool_tables:
                if table not in allowed_tables:
                    write_audit_entry({
                        "agent_id": agent_id,
                        "event_type": "TOOL_CALL",
                        "tool_name": tool_name,
                        "scope": tool_scope,
                        "args": safe_args,
                        "kwargs": safe_kwargs,
                        "decision": "DENIED",
                        "reason": (
                            f"Tool accesses table '{table}' which is not "
                            f"in allowed_tables {allowed_tables}"
                        ),
                    })
                    return (
                        f"BLOCKED BY POLICY: agent '{agent_id}' cannot use "
                        f"tool '{tool_name}' (table '{table}' not allowed)."
                    )

        # Check PII access
        if not pii_allowed and rule.get("contains_pii", False):
            write_audit_entry({
                "agent_id": agent_id,
                "event_type": "TOOL_CALL",
                "tool_name": tool_name,
                "scope": tool_scope,
                "args": safe_args,
                "kwargs": safe_kwargs,
                "decision": "DENIED",
                "reason": "Tool contains PII but pii_allowed=false",
            })
            return (
                f"BLOCKED BY POLICY: agent '{agent_id}' cannot use "
                f"tool '{tool_name}' (PII access not permitted)."
            )

        # ---- Check 5: rate limit ----
        _call_counters[counter_key] = _call_counters.get(counter_key, 0) + 1
        max_calls = policy.get("rate_limits", {}).get("max_calls_per_tool", 999)
        if _call_counters[counter_key] > max_calls:
            write_audit_entry({
                "agent_id": agent_id,
                "event_type": "TOOL_CALL",
                "tool_name": tool_name,
                "scope": tool_scope,
                "args": safe_args,
                "kwargs": safe_kwargs,
                "decision": "RATE_LIMITED",
                "reason": f"Rate limit exceeded (max {max_calls} calls)",
            })
            return (
                f"BLOCKED BY POLICY: rate limit exceeded for "
                f"tool '{tool_name}' (max {max_calls})."
            )

        # ---- ALL checks passed - run the real tool ----
        result = original_function(*args, **kwargs)

        output_preview = str(result)[:500] if log_outputs else "[redacted]"
        write_audit_entry({
            "agent_id": agent_id,
            "event_type": "TOOL_CALL",
            "tool_name": tool_name,
            "scope": tool_scope,
            "args": safe_args,
            "kwargs": safe_kwargs,
            "output_preview": output_preview,
            "decision": "ALLOWED",
        })

        return result

    return wrapped_function
