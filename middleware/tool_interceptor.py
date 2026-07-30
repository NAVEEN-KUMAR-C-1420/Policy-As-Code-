"""
Tool Interception Middleware
==============================
This is the heart of the AI governance layer.

Every single tool in this project is wrapped with guard_tool() before
it is handed to a LangChain agent. That means NO tool call ever runs
directly - it always passes through this checkpoint first, which:

  1. Looks up the tool's rule in the agent's policy.yaml
  2. Blocks the call if the tool is not explicitly allowed
  3. Blocks the call if the agent has exceeded its rate limit
  4. Runs the real tool only if both checks pass
  5. Writes an audit log entry either way (ALLOWED or BLOCKED)

This is what lets you "validate and build on policy and AI governance":
policy.yaml is not just documentation, it is actually enforced here at
runtime, and every decision is recorded in logs/audit_log.jsonl.
"""

import functools

from middleware.audit_log import write_audit_entry

# Keeps track of how many times each (agent, tool) pair has been called
# during this run, so we can enforce simple rate limits.
call_counters = {}


def _find_tool_rule(policy: dict, tool_name: str):
    """Look up the policy rule for one specific tool name."""
    for rule in policy.get("allowed_tools", []):
        if rule.get("name") == tool_name:
            return rule
    return None


def guard_tool(tool_name: str, policy: dict, agent_id: str, original_function):
    """
    Wrap a plain python function (the real tool logic) with a policy
    check and audit logging.

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

        counter_key = f"{agent_id}:{tool_name}"
        call_counters[counter_key] = call_counters.get(counter_key, 0) + 1

        # ---- Check 1: is this tool allowed at all? ----
        if rule is None or rule.get("allowed") is False:
            write_audit_entry({
                "agent_id": agent_id,
                "tool_name": tool_name,
                "args": str(args),
                "kwargs": str(kwargs),
                "decision": "BLOCKED",
                "reason": "Tool not permitted by policy.yaml",
            })
            return (
                f"BLOCKED BY POLICY: agent '{agent_id}' is not allowed "
                f"to use tool '{tool_name}'."
            )

        # ---- Check 2: has the rate limit been exceeded? ----
        max_calls = policy.get("rate_limits", {}).get("max_calls_per_tool", 999)
        if call_counters[counter_key] > max_calls:
            write_audit_entry({
                "agent_id": agent_id,
                "tool_name": tool_name,
                "args": str(args),
                "kwargs": str(kwargs),
                "decision": "BLOCKED",
                "reason": f"Rate limit exceeded (max {max_calls} calls)",
            })
            return f"BLOCKED BY POLICY: rate limit exceeded for tool '{tool_name}'."

        # ---- Both checks passed - run the real tool ----
        result = original_function(*args, **kwargs)

        write_audit_entry({
            "agent_id": agent_id,
            "tool_name": tool_name,
            "scope": rule.get("scope"),
            "args": str(args),
            "kwargs": str(kwargs),
            "output_preview": str(result)[:500],
            "decision": "ALLOWED",
        })

        return result

    return wrapped_function
