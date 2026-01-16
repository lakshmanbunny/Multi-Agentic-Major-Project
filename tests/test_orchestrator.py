"""
Tests for orchestrator service
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "libs" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "orchestrator"))

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns service info"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "orchestrator"
    assert data["version"] == "0.1.0"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_start_workflow():
    """Test starting a new workflow"""
    request_data = {
        "user_goal": "Build a classification model",
        "dataset_url": "https://example.com/data.csv"
    }
    
    response = client.post("/workflow/start", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "workflow_id" in data
    assert data["status"] == "started"
    assert data["workflow_id"].startswith("wf-")


def test_get_workflow_status():
    """Test getting workflow status"""
    # First create a workflow
    request_data = {
        "user_goal": "Test workflow",
        "dataset_url": ""
    }
    
    create_response = client.post("/workflow/start", json=request_data)
    workflow_id = create_response.json()["workflow_id"]
    
    # Now get its status
    response = client.get(f"/workflow/{workflow_id}/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == workflow_id
    assert "status" in data
    assert "current_step" in data


def test_approve_workflow_step():
    """Test approving a workflow step"""
    # Create a workflow first
    request_data = {"user_goal": "Test approval"}
    create_response = client.post("/workflow/start", json=request_data)
    workflow_id = create_response.json()["workflow_id"]
    
    # Approve it
    response = client.post(f"/workflow/{workflow_id}/approve")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


def test_reject_workflow_step():
    """Test rejecting a workflow step"""
    # Create a workflow first
    request_data = {"user_goal": "Test rejection"}
    create_response = client.post("/workflow/start", json=request_data)
    workflow_id = create_response.json()["workflow_id"]
    
    # Reject it
    response = client.post(f"/workflow/{workflow_id}/reject")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"


def test_list_workflows():
    """Test listing all workflows"""
    # Create a couple of workflows
    client.post("/workflow/start", json={"user_goal": "Test 1"})
    client.post("/workflow/start", json={"user_goal": "Test 2"})
    
    # List them
    response = client.get("/workflows")
    
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "workflows" in data
    assert data["count"] >= 2


def test_workflow_not_found():
    """Test accessing non-existent workflow"""
    response = client.get("/workflow/wf-nonexistent/status")
    
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
