import json

from common.db import run_query, run_write


class AuditRepository:
    @staticmethod
    def save(entry: dict):
        run_write(
            """INSERT INTO audit_logs 
               (timestamp, agent_name, tool_name, action, decision, reason, policy_version, risk_score, execution_time, status, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry.get("timestamp"),
                entry.get("agent_id", entry.get("agent_name")),
                entry.get("tool_name"),
                entry.get("action", entry.get("event_type")),
                entry.get("decision"),
                entry.get("reason"),
                entry.get("policy_version"),
                entry.get("risk_score"),
                entry.get("execution_time"),
                entry.get("status"),
                json.dumps(entry.get("metadata", {})),
            ),
        )

    @staticmethod
    def get_recent(limit: int = 50) -> list:
        rows = run_query("SELECT * FROM audit_logs ORDER BY audit_id DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows][
            ::-1
        ]  # Return in chronological order if desired, or as is. Usually recent is desc, but let's just return what we got.


class ReportRepository:
    @staticmethod
    def save_report_content(
        account_id: int, content: str, summary: str = "", generated_by: str = "", metadata: dict = None
    ):
        run_write(
            """INSERT INTO reports (account_id, report_content, summary, created_at, generated_by, metadata)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)""",
            (account_id, content, summary, generated_by, json.dumps(metadata or {})),
        )


class ConversationRepository:
    @staticmethod
    def save(conversation_id: str, user_message: str, assistant_response: str, session_id: str = ""):
        run_write(
            """INSERT INTO conversations (conversation_id, user_message, assistant_response, created_at, status, session_id)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'COMPLETED', ?)""",
            (conversation_id, user_message, assistant_response, session_id),
        )


class ToolExecutionRepository:
    @staticmethod
    def save(entry: dict):
        run_write(
            """INSERT INTO tool_executions (conversation_id, tool_name, allowed, blocked, reason, risk_score, policy_version, duration, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                entry.get("conversation_id"),
                entry.get("tool_name"),
                1 if entry.get("allowed") else 0,
                1 if entry.get("blocked") else 0,
                entry.get("reason"),
                entry.get("risk_score"),
                entry.get("policy_version"),
                entry.get("duration"),
            ),
        )


class HITLRepository:
    @staticmethod
    def save_request(entry: dict):
        return run_write(
            """INSERT INTO hitl_requests (conversation_id, tool_name, risk_score, threshold, status, created_at, reason)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?) RETURNING request_id""",
            (
                entry.get("conversation_id"),
                entry.get("tool_name"),
                entry.get("risk_score"),
                entry.get("threshold"),
                entry.get("status", "PENDING_HUMAN_APPROVAL"),
                entry.get("reason"),
            ),
        )

    @staticmethod
    def get_request(request_id: int) -> dict:
        rows = run_query("SELECT * FROM hitl_requests WHERE request_id = ?", (request_id,))
        return dict(rows[0]) if rows else None

    @staticmethod
    def update_status(request_id: int, status: str, approved_by: str = ""):
        run_write(
            """UPDATE hitl_requests SET status = ?, approved_by = ?, approval_time = CURRENT_TIMESTAMP WHERE request_id = ?""",
            (status, approved_by, request_id),
        )


class GovernanceRepository:
    @staticmethod
    def log_event(event_type: str, description: str, agent: str = "", policy_version: str = "", metadata: dict = None):
        run_write(
            """INSERT INTO governance_events (event_type, description, agent, policy_version, created_at, metadata)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)""",
            (event_type, description, agent, policy_version, json.dumps(metadata or {})),
        )


class GovernanceVersionRepository:
    @staticmethod
    def create_version(version_data: dict) -> int:
        return run_write(
            """INSERT INTO governance_versions 
               (version_number, git_commit_sha, git_branch, policy_hash, agent_hash, governance_hash, change_summary, created_at, created_by, deployment_status, is_active, rolled_back_from, rollback_timestamp, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?)""",
            (
                version_data.get("version_number"),
                version_data.get("git_commit_sha"),
                version_data.get("git_branch"),
                version_data.get("policy_hash"),
                version_data.get("agent_hash"),
                version_data.get("governance_hash"),
                version_data.get("change_summary"),
                version_data.get("created_by", "system"),
                version_data.get("deployment_status", "DEPLOYED"),
                1 if version_data.get("is_active") else 0,
                version_data.get("rolled_back_from"),
                version_data.get("rollback_timestamp"),
                json.dumps(version_data.get("metadata", {})),
            ),
        )

    @staticmethod
    def deactivate_all():
        run_write("UPDATE governance_versions SET is_active = 0", ())

    @staticmethod
    def _parse_row(row: dict) -> dict:
        if not row:
            return row
        if "metadata" in row and isinstance(row["metadata"], str):
            try:
                row["metadata"] = json.loads(row["metadata"])
            except:
                row["metadata"] = {}
        return row

    @staticmethod
    def get_latest_version() -> dict:
        rows = run_query("SELECT * FROM governance_versions ORDER BY version_number DESC LIMIT 1", ())
        return GovernanceVersionRepository._parse_row(dict(rows[0])) if rows else None

    @staticmethod
    def get_active_version() -> dict:
        rows = run_query("SELECT * FROM governance_versions WHERE is_active = 1 LIMIT 1", ())
        return GovernanceVersionRepository._parse_row(dict(rows[0])) if rows else None

    @staticmethod
    def get_all_versions() -> list:
        rows = run_query("SELECT * FROM governance_versions ORDER BY version_number DESC, created_at DESC", ())
        seen = set()
        unique_versions = []
        for r in rows:
            v_num = r.get("version_number")
            if v_num not in seen:
                seen.add(v_num)
                unique_versions.append(GovernanceVersionRepository._parse_row(dict(r)))
        return unique_versions

    @staticmethod
    def get_version(version_number: int) -> dict:
        rows = run_query("SELECT * FROM governance_versions WHERE version_number = ? LIMIT 1", (version_number,))
        return GovernanceVersionRepository._parse_row(dict(rows[0])) if rows else None

    @staticmethod
    def get_by_commit(commit_sha: str) -> dict:
        rows = run_query(
            "SELECT * FROM governance_versions WHERE git_commit_sha = ? ORDER BY version_number DESC LIMIT 1",
            (commit_sha,),
        )
        return GovernanceVersionRepository._parse_row(dict(rows[0])) if rows else None

    @staticmethod
    def get_by_hashes(policy_hash: str, agent_hash: str, governance_hash: str) -> dict:
        rows = run_query(
            "SELECT * FROM governance_versions WHERE policy_hash = ? AND agent_hash = ? AND governance_hash = ? ORDER BY version_number DESC LIMIT 1",
            (policy_hash, agent_hash, governance_hash),
        )
        return GovernanceVersionRepository._parse_row(dict(rows[0])) if rows else None

    @staticmethod
    def set_active_version(version_number: int, rolled_back_from: int = None):
        run_write("UPDATE governance_versions SET is_active = 0", ())
        if rolled_back_from:
            run_write(
                "UPDATE governance_versions SET is_active = 1, rolled_back_from = ?, rollback_timestamp = CURRENT_TIMESTAMP WHERE version_number = ?",
                (rolled_back_from, version_number),
            )
        else:
            run_write("UPDATE governance_versions SET is_active = 1 WHERE version_number = ?", (version_number,))
