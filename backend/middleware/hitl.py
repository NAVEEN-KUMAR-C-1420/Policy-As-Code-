"""
Human-in-the-Loop (HITL) Module
=================================
Simple, demonstrable HITL mechanism for the governance framework.

This module does NOT build a frontend. It provides:
  1. A function to check whether HITL approval is required based on
     the policy's risk_threshold and the calculated risk score.
  2. A structured result indicating whether the pipeline should
     continue or pause for human approval.
  3. A CLI-based approval path for demonstrations.

Usage:
    from middleware.hitl import check_hitl, request_cli_approval
    result = check_hitl(risk_score=0.85, policy=policy)
    if result["approval_required"]:
        approved = request_cli_approval(result)
"""

from middleware.audit_log import write_audit_entry


def check_hitl(risk_score: float, policy: dict, agent_id: str = "") -> dict:
    """
    Check whether a risk score requires human approval.

    Parameters:
        risk_score  - normalized risk score from 0.0 to 1.0
        policy      - the agent's policy dictionary
        agent_id    - the agent's ID (for audit logging)

    Returns a dictionary:
        {
            "approval_required": bool,
            "status": "APPROVED" | "PENDING_HUMAN_APPROVAL",
            "risk_score": float,
            "risk_threshold": float,
            "hitl_enabled": bool,
        }
    """
    hitl_config = policy.get("hitl", {})
    hitl_enabled = hitl_config.get("enabled", False)
    risk_threshold = hitl_config.get("risk_threshold", 1.0)
    high_risk_requires_approval = hitl_config.get("high_risk_requires_approval", False)

    result = {
        "approval_required": False,
        "status": "APPROVED",
        "risk_score": risk_score,
        "risk_threshold": risk_threshold,
        "hitl_enabled": hitl_enabled,
    }

    if hitl_enabled and high_risk_requires_approval and risk_score > risk_threshold:
        result["approval_required"] = True
        result["status"] = "PENDING_HUMAN_APPROVAL"

        write_audit_entry(
            {
                "agent_id": agent_id,
                "event_type": "HITL_CHECK",
                "decision": "HITL_REQUIRED",
                "reason": (f"Risk score {risk_score:.2f} exceeds threshold " f"{risk_threshold:.2f}"),
                "risk_score": risk_score,
                "risk_threshold": risk_threshold,
            }
        )

        from common.repositories import HITLRepository

        HITLRepository.save_request(
            {
                "conversation_id": "system_generated",
                "tool_name": "unknown_tool",
                "risk_score": risk_score,
                "threshold": risk_threshold,
                "status": "PENDING_HUMAN_APPROVAL",
                "reason": f"Risk score {risk_score:.2f} exceeds threshold {risk_threshold:.2f}",
            }
        )
    else:
        write_audit_entry(
            {
                "agent_id": agent_id,
                "event_type": "HITL_CHECK",
                "decision": "ALLOWED",
                "reason": (
                    f"Risk score {risk_score:.2f} is within threshold " f"{risk_threshold:.2f}"
                    if hitl_enabled
                    else "HITL is not enabled for this agent"
                ),
                "risk_score": risk_score,
                "risk_threshold": risk_threshold,
            }
        )

    return result


def request_cli_approval(hitl_result: dict) -> bool:
    """
    Request human approval via CLI prompt.

    This is for demo/hackathon use. It prints the risk details
    and waits for the user to type 'yes' or 'no'.

    Returns True if approved, False if rejected.
    """
    print("\n" + "=" * 60)
    print("  HUMAN-IN-THE-LOOP APPROVAL REQUIRED")
    print("=" * 60)
    print(f"  Risk Score:     {hitl_result['risk_score']:.2f}")
    print(f"  Risk Threshold: {hitl_result['risk_threshold']:.2f}")
    print(f"  Status:         {hitl_result['status']}")
    print("=" * 60)

    while True:
        answer = input("\n  Approve this high-risk operation? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            print("  ✓ Approved by human operator.\n")
            return True
        elif answer in ("no", "n"):
            print("  ✗ Rejected by human operator.\n")
            return False
        else:
            print("  Please enter 'yes' or 'no'.")
