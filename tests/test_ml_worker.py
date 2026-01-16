"""
Tests for ML Worker service
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "libs" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "ml_worker"))

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
    assert data["service"] == "ml_worker"
    assert data["version"] == "0.1.0"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_algorithms():
    """Test listing supported algorithms"""
    response = client.get("/algorithms")
    
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert "regression" in data
    assert "RandomForestClassifier" in data["classification"]
    assert "LogisticRegression" in data["classification"]


# Note: The following tests require actual datasets
# In production, use fixtures with sample datasets

@pytest.mark.skip(reason="Requires dataset file")
def test_train_model():
    """Test model training"""
    request_data = {
        "dataset_path": "/data/test_dataset.csv",
        "target_column": "target",
        "algorithm": "RandomForestClassifier",
        "test_size": 0.2,
        "random_state": 42
    }
    
    response = client.post("/train", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "model_id" in data
    assert "metrics" in data
    assert "accuracy" in data["metrics"]


@pytest.mark.skip(reason="Requires dataset file and takes time")
def test_optimize_hyperparameters():
    """Test hyperparameter optimization"""
    request_data = {
        "dataset_path": "/data/test_dataset.csv",
        "target_column": "target",
        "algorithm": "RandomForestClassifier",
        "n_trials": 10  # Small number for testing
    }
    
    response = client.post("/optimize", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "study_id" in data
    assert "best_params" in data
    assert "best_score" in data


@pytest.mark.skip(reason="Requires trained model")
def test_evaluate_model():
    """Test model evaluation"""
    model_id = "model-test-123"
    
    response = client.get(f"/model/{model_id}/evaluate")
    
    # This would fail with 404 if model doesn't exist
    # In real test, first train a model, then evaluate it
    assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
