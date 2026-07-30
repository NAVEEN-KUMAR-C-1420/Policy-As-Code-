def get_overall_stats() -> dict:
    return {"total_runs": 100, "success_rate": "98%"}

def get_agent_stats() -> dict:
    return {"data_collector_agent": {"runs": 100}}

def get_tool_stats() -> dict:
    return {"read_account_transactions": {"calls": 200}}

def get_policy_stats() -> dict:
    return {"active_policies": 3, "violations_blocked": 15}
