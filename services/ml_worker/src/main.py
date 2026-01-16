"""
ML Worker Service - The Muscle 💪

FastAPI service that handles machine learning model training,
hyperparameter optimization with Optuna, and model evaluation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from core import setup_logger

# Initialize logger
logger = setup_logger("ml_worker", level="INFO")

# Initialize FastAPI app
app = FastAPI(
    title="Auto-DataScientist ML Worker",
    description="Machine learning training and optimization service",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class TrainRequest(BaseModel):
    """Request to train a model"""
    dataset_path: str
    target_column: str
    algorithm: str = "RandomForestClassifier"
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)
    random_state: int = 42
    
    class Config:
        json_schema_extra = {
            "example": {
                "dataset_path": "/data/churn.csv",
                "target_column": "Churn",
                "algorithm": "RandomForestClassifier",
                "test_size": 0.2,
                "random_state": 42
            }
        }


class OptimizeRequest(BaseModel):
    """Request to optimize hyperparameters"""
    dataset_path: str
    target_column: str
    algorithm: str = "RandomForestClassifier"
    n_trials: int = Field(default=100, ge=10, le=1000)
    timeout: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "dataset_path": "/data/churn.csv",
                "target_column": "Churn",
                "algorithm": "RandomForestClassifier",
                "n_trials": 100
            }
        }


class TrainResponse(BaseModel):
    """Response from training"""
    success: bool
    model_id: str = ""
    metrics: Dict[str, float] = {}
    message: str


class OptimizeResponse(BaseModel):
    """Response from optimization"""
    success: bool
    study_id: str = ""
    best_params: Dict = {}
    best_score: float = 0.0
    n_trials: int = 0


class EvaluateResponse(BaseModel):
    """Response from evaluation"""
    metrics: Dict[str, float]
    confusion_matrix: List[List[int]] = []
    classification_report: str = ""


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - service info"""
    return HealthResponse(
        status="healthy",
        service="ml_worker",
        version="0.1.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    
    return HealthResponse(
        status="healthy",
        service="ml_worker",
        version="0.1.0"
    )


@app.post("/train", response_model=TrainResponse)
async def train_model(request: TrainRequest):
    """
    Train a machine learning model
    
    This endpoint trains a model on the provided dataset using
    the specified algorithm and returns evaluation metrics.
    """
    logger.info(
        "Training model",
        algorithm=request.algorithm,
        dataset=request.dataset_path
    )
    
    try:
        from .trainer import ModelTrainer
        
        trainer = ModelTrainer()
        result = await trainer.train(
            dataset_path=request.dataset_path,
            target_column=request.target_column,
            algorithm=request.algorithm,
            test_size=request.test_size,
            random_state=request.random_state
        )
        
        logger.info(
            "Model trained successfully",
            model_id=result["model_id"],
            accuracy=result["metrics"].get("accuracy", 0.0)
        )
        
        return TrainResponse(
            success=True,
            model_id=result["model_id"],
            metrics=result["metrics"],
            message="Model trained successfully"
        )
    
    except Exception as e:
        logger.error("Failed to train model", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to train model: {str(e)}")


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_hyperparameters(request: OptimizeRequest):
    """
    Optimize model hyperparameters using Optuna
    
    This endpoint runs hyperparameter optimization using Optuna's
    TPE sampler to find the best hyperparameters for the model.
    """
    logger.info(
        "Starting hyperparameter optimization",
        algorithm=request.algorithm,
        n_trials=request.n_trials
    )
    
    try:
        from .optuna_optimizer import OptunaOptimizer
        
        optimizer = OptunaOptimizer()
        result = await optimizer.optimize(
            dataset_path=request.dataset_path,
            target_column=request.target_column,
            algorithm=request.algorithm,
            n_trials=request.n_trials,
            timeout=request.timeout
        )
        
        logger.info(
            "Optimization completed",
            study_id=result["study_id"],
            best_score=result["best_score"],
            n_trials=result["n_trials"]
        )
        
        return OptimizeResponse(
            success=True,
            study_id=result["study_id"],
            best_params=result["best_params"],
            best_score=result["best_score"],
            n_trials=result["n_trials"]
        )
    
    except Exception as e:
        logger.error("Optimization failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/model/{model_id}/evaluate", response_model=EvaluateResponse)
async def evaluate_model(model_id: str):
    """
    Evaluate a trained model
    
    Returns detailed evaluation metrics including confusion matrix
    and classification report.
    """
    logger.info("Evaluating model", model_id=model_id)
    
    try:
        from .evaluator import ModelEvaluator
        
        evaluator = ModelEvaluator()
        metrics = await evaluator.evaluate(model_id)
        
        logger.info("Model evaluated", model_id=model_id, accuracy=metrics.get("accuracy", 0.0))
        
        return EvaluateResponse(
            metrics=metrics.get("metrics", {}),
            confusion_matrix=metrics.get("confusion_matrix", []),
            classification_report=metrics.get("classification_report", "")
        )
    
    except Exception as e:
        logger.error("Evaluation failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found or evaluation failed")


@app.get("/algorithms")
async def list_algorithms():
    """List supported ML algorithms"""
    algorithms = {
        "classification": [
            "RandomForestClassifier",
            "LogisticRegression",
            "GradientBoostingClassifier",
            "XGBClassifier",
            "SVC"
        ],
        "regression": [
            "RandomForestRegressor",
            "LinearRegression",
            "GradientBoostingRegressor",
            "XGBRegressor"
        ]
    }
    
    return algorithms


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting ML Worker service")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
