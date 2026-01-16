
from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DatasetInfo(TypedDict):
    url: str
    file_path: str
    is_public: bool
    description: str

class CodeContext(TypedDict):
    eda_code: str
    model_code: str
    file_name: str

class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    user_goal: str
    dataset_info: DatasetInfo
    research_plan: List[str]
    code_context: CodeContext
    review_feedback: List[str]
    human_approval: ApprovalStatus
    next_step: str
    rejected_urls: List[str]  # Track rejected dataset URLs for retry exclusion

