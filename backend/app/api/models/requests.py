from typing import Any

from pydantic import BaseModel


class PipelineRunRequest(BaseModel):
    account_id: int
    auto_approve_hitl: bool = False


class AgentRunRequest(BaseModel):
    input_data: dict[str, Any]


class PolicyValidateRequest(BaseModel):
    policy_yaml_content: str


class PolicyDeployRequest(BaseModel):
    agent_id: str
    policy_yaml_content: str
    commit_sha: str | None = None


class PolicyRollbackRequest(BaseModel):
    commit_sha: str


class PolicyDiffRequest(BaseModel):
    agent_id: str
    commit_sha: str


class AuditSearchRequest(BaseModel):
    event_type: str | None = None
    agent_id: str | None = None
    decision: str | None = None
    limit: int = 50
