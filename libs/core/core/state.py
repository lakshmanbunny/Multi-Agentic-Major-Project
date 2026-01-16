"""
Shared State Models for LangGraph Workflows

This module defines the core state structure used across all agents
in the Auto-DataScientist system.
"""

from enum import Enum
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    """Human approval status for workflow steps"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DatasetInfo(BaseModel):
    """Information about the dataset being processed"""
    url: str = Field(default="", description="URL or source of the dataset")
    file_path: str = Field(default="", description="Local file path after download")
    is_public: bool = Field(default=True, description="Whether dataset is publicly accessible")
    description: str = Field(default="", description="Dataset description and metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/dataset.csv",
                "file_path": "/data/dataset.csv",
                "is_public": True,
                "description": "Customer churn dataset with 10k records"
            }
        }


class CodeContext(BaseModel):
    """Current generated code context across workflow"""
    eda_code: str = Field(default="", description="Generated EDA/data cleaning code")
    model_code: str = Field(default="", description="Generated model training code")
    file_name: str = Field(default="", description="Name of the current notebook/script")

    class Config:
        json_schema_extra = {
            "example": {
                "eda_code": "import pandas as pd\ndf = pd.read_csv('data.csv')",
                "model_code": "from sklearn.ensemble import RandomForestClassifier",
                "file_name": "ml_pipeline.ipynb"
            }
        }


class AgentState(TypedDict):
    """
    Main state structure for the LangGraph workflow.
    
    This TypedDict defines all state keys that will be passed between agents.
    Uses the `add_messages` reducer for conversation history management.
    """
    # Conversation history with add_messages reducer for automatic message aggregation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Original user goal/prompt
    user_goal: str
    
    # Dataset information
    dataset_info: DatasetInfo
    
    # Research plan steps from Research Agent
    research_plan: list[str]
    
    # Code generation context
    code_context: CodeContext
    
    # Feedback from Critic Agent
    review_feedback: list[str]
    
    # Human approval status for manual review steps
    human_approval: ApprovalStatus
    
    # Next agent to execute in the workflow
    next_step: str
