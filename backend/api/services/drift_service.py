def get_drift_report() -> dict:
    return {"agents_drifting": 0, "details": []}


def get_agent_drift(agent_id: str) -> dict:
    return {"agent_id": agent_id, "drift_detected": False}


def check_drift() -> dict:
    return {"expected_policy": "...", "runtime_policy": "...", "differences": [], "status": "in_sync"}
