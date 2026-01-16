"""
Tests for browser agent service
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "libs" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "browser_agent"))

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
    assert data["service"] == "browser_agent"
    assert data["version"] == "0.1.0"
    assert "browser_ready" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["browser_ready"] is not None


# Note: The following tests require actual browser/Colab interaction
# In production, use mocks or integration test environment

@pytest.mark.skip(reason="Requires actual browser instance")
def test_open_colab():
    """Test opening Google Colab"""
    request_data = {
        "notebook_name": "test_notebook.ipynb"
    }
    
    response = client.post("/colab/open", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "notebook_url" in data


@pytest.mark.skip(reason="Requires active Colab session")
def test_execute_code():
    """Test code execution in Colab"""
    request_data = {
        "code": "print('Hello, World!')",
        "notebook_name": "test.ipynb",
        "wait_for_output": True
    }
    
    response = client.post("/colab/execute", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "output" in data


@pytest.mark.skip(reason="Requires active Colab session")
def test_close_colab():
    """Test closing Colab session"""
    response = client.post("/colab/close")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.skip(reason="Requires network access")
def test_download_dataset():
    """Test dataset download"""
    response = client.post(
        "/dataset/download",
        params={
            "url": "https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv",
            "destination": "/tmp/test_dataset.csv"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "file_path" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
