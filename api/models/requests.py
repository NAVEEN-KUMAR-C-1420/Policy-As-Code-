from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class PipelineRunRequest(BaseModel):
    account_id: int
    auto_approve_hitl: bool = False

class AgentRunRequest(BaseModel):
    input_data: Dict[str, Any]

class PolicyValidateRequest(BaseModel):
    policy_yaml_content: str

class PolicyDeployRequest(BaseModel):
    agent_id: str
    policy_yaml_content: str
    commit_sha: Optional[str] = None

class PolicyRollbackRequest(BaseModel):
    commit_sha: str

class PolicyDiffRequest(BaseModel):
    agent_id: str
    commit_sha: str

class AuditSearchRequest(BaseModel):
    event_type: Optional[str] = None
    agent_id: Optional[str] = None
    decision: Optional[str] = None
    limit: int = 50
