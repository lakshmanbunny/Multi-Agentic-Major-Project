"""
Tests for core library state models
"""

import sys
from pathlib import Path

# Add libs/core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "libs" / "core"))

import pytest
from langchain_core.messages import HumanMessage, AIMessage

from core import AgentState, DatasetInfo, CodeContext, ApprovalStatus


def test_dataset_info_creation():
    """Test DatasetInfo model creation and validation"""
    dataset = DatasetInfo(
        url="https://example.com/data.csv",
        file_path="/data/dataset.csv",
        is_public=True,
        description="Test dataset"
    )
    
    assert dataset.url == "https://example.com/data.csv"
    assert dataset.file_path == "/data/dataset.csv"
    assert dataset.is_public is True
    assert dataset.description == "Test dataset"


def test_dataset_info_defaults():
    """Test DatasetInfo default values"""
    dataset = DatasetInfo()
    
    assert dataset.url == ""
    assert dataset.file_path == ""
    assert dataset.is_public is True
    assert dataset.description == ""


def test_code_context_creation():
    """Test CodeContext model creation"""
    code_ctx = CodeContext(
        eda_code="import pandas as pd",
        model_code="from sklearn.ensemble import RandomForestClassifier",
        file_name="pipeline.ipynb"
    )
    
    assert code_ctx.eda_code == "import pandas as pd"
    assert code_ctx.model_code == "from sklearn.ensemble import RandomForestClassifier"
    assert code_ctx.file_name == "pipeline.ipynb"


def test_code_context_defaults():
    """Test CodeContext default values"""
    code_ctx = CodeContext()
    
    assert code_ctx.eda_code == ""
    assert code_ctx.model_code == ""
    assert code_ctx.file_name == ""


def test_approval_status_enum():
    """Test ApprovalStatus enum values"""
    assert ApprovalStatus.PENDING == "PENDING"
    assert ApprovalStatus.APPROVED == "APPROVED"
    assert ApprovalStatus.REJECTED == "REJECTED"
    
    # Test enum membership
    assert ApprovalStatus.PENDING in ApprovalStatus
    assert "INVALID" not in [status.value for status in ApprovalStatus]


def test_agent_state_structure():
    """Test AgentState TypedDict structure"""
    # Create a valid AgentState
    state: AgentState = {
        "messages": [
            HumanMessage(content="Build a classification model"),
            AIMessage(content="I'll help you build that model")
        ],
        "user_goal": "Build a classification model for customer churn",
        "dataset_info": DatasetInfo(
            url="https://example.com/churn.csv",
            file_path="/data/churn.csv",
            is_public=True,
            description="Customer churn dataset"
        ),
        "research_plan": [
            "Download dataset",
            "Perform EDA",
            "Train baseline model"
        ],
        "code_context": CodeContext(
            eda_code="df = pd.read_csv('/data/churn.csv')",
            model_code="model = RandomForestClassifier()",
            file_name="churn_analysis.ipynb"
        ),
        "review_feedback": [
            "Good feature selection",
            "Consider hyperparameter tuning"
        ],
        "human_approval": ApprovalStatus.PENDING,
        "next_step": "data_engineering_agent"
    }
    
    # Validate state structure
    assert len(state["messages"]) == 2
    assert state["user_goal"] == "Build a classification model for customer churn"
    assert state["dataset_info"].url == "https://example.com/churn.csv"
    assert len(state["research_plan"]) == 3
    assert state["code_context"].file_name == "churn_analysis.ipynb"
    assert len(state["review_feedback"]) == 2
    assert state["human_approval"] == ApprovalStatus.PENDING
    assert state["next_step"] == "data_engineering_agent"


def test_pydantic_validation():
    """Test that Pydantic validation works correctly"""
    # Valid dataset
    dataset = DatasetInfo(
        url="https://example.com/data.csv",
        is_public=True
    )
    assert dataset.url == "https://example.com/data.csv"
    
    # Test that boolean conversion works
    dataset_with_str_bool = DatasetInfo(
        url="test.csv",
        is_public="true"  # type: ignore
    )
    # Pydantic will coerce this to boolean
    assert isinstance(dataset_with_str_bool.is_public, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
