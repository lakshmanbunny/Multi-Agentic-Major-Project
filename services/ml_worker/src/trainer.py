"""
Model Trainer

Handles machine learning model training with various algorithms.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import joblib
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from core import setup_logger

logger = setup_logger("model_trainer", level="INFO")


class ModelTrainer:
    """
    Train machine learning models with various algorithms
    
    Supports classification and regression tasks with
    popular scikit-learn algorithms.
    """
    
    # Algorithm mapping
    ALGORITHMS = {
        "RandomForestClassifier": RandomForestClassifier,
        "LogisticRegression": LogisticRegression,
        "GradientBoostingClassifier": GradientBoostingClassifier,
        "SVC": SVC,
        "RandomForestRegressor": RandomForestRegressor,
        "LinearRegression": LinearRegression,
    }
    
    def __init__(self, models_dir: str = "./models"):
        """
        Initialize trainer
        
        Args:
            models_dir: Directory to save trained models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Store model metadata
        self.model_metadata: Dict[str, dict] = {}
        
        logger.info("ModelTrainer initialized", models_dir=str(self.models_dir))
    
    async def train(
        self,
        dataset_path: str,
        target_column: str,
        algorithm: str = "RandomForestClassifier",
        test_size: float = 0.2,
        random_state: int = 42,
        hyperparams: Optional[Dict] = None
    ) -> Dict:
        """
        Train a model
        
        Args:
            dataset_path: Path to dataset CSV file
            target_column: Name of target column
            algorithm: Algorithm name
            test_size: Proportion of test set
            random_state: Random seed
            hyperparams: Optional hyperparameters
        
        Returns:
            Dict with model_id, metrics, and metadata
        """
        logger.info(
            "Starting model training",
            algorithm=algorithm,
            dataset=dataset_path
        )
        
        try:
            # Load dataset
            df = pd.read_csv(dataset_path)
            logger.info("Dataset loaded", shape=df.shape)
            
            # Prepare features and target
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            logger.info(
                "Data split",
                train_size=len(X_train),
                test_size=len(X_test)
            )
            
            # Get algorithm class
            if algorithm not in self.ALGORITHMS:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            AlgorithmClass = self.ALGORITHMS[algorithm]
            
            # Initialize model with hyperparameters
            if hyperparams:
                model = AlgorithmClass(**hyperparams)
            else:
                model = AlgorithmClass(random_state=random_state)
            
            # Train model
            start_time = datetime.utcnow()
            model.fit(X_train, y_train)
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info("Model trained", training_time=training_time)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = self._calculate_metrics(y_test, y_pred, algorithm)
            
            # Generate model ID
            model_id = f"model-{uuid.uuid4().hex[:12]}"
            
            # Save model
            model_path = self.models_dir / f"{model_id}.joblib"
            joblib.dump(model, model_path)
            
            # Save metadata
            metadata = {
                "model_id": model_id,
                "algorithm": algorithm,
                "dataset_path": dataset_path,
                "target_column": target_column,
                "created_at": datetime.utcnow().isoformat(),
                "training_time": training_time,
                "test_size": test_size,
                "random_state": random_state,
                "hyperparams": hyperparams or {},
                "metrics": metrics,
                "model_path": str(model_path)
            }
            
            self.model_metadata[model_id] = metadata
            
            logger.info(
                "Model saved",
                model_id=model_id,
                accuracy=metrics.get("accuracy", metrics.get("r2_score", 0.0))
            )
            
            return {
                "model_id": model_id,
                "metrics": metrics,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error("Training failed", error=str(e), exc_info=True)
            raise
    
    def _calculate_metrics(self, y_true, y_pred, algorithm: str) -> Dict[str, float]:
        """
        Calculate evaluation metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            algorithm: Algorithm name
        
        Returns:
            Dict of metrics
        """
        metrics = {}
        
        # Check if classification or regression
        is_classification = any(
            clf in algorithm for clf in ["Classifier", "SVC"]
        )
        
        if is_classification:
            # Classification metrics
            metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
            
            # Get precision, recall, f1 from classification report
            report = classification_report(y_true, y_pred, output_dict=True)
            metrics["precision"] = float(report["weighted avg"]["precision"])
            metrics["recall"] = float(report["weighted avg"]["recall"])
            metrics["f1_score"] = float(report["weighted avg"]["f1-score"])
        
        else:
            # Regression metrics
            metrics["mse"] = float(mean_squared_error(y_true, y_pred))
            metrics["rmse"] = float(mean_squared_error(y_true, y_pred, squared=False))
            metrics["r2_score"] = float(r2_score(y_true, y_pred))
        
        return metrics
    
    def load_model(self, model_id: str):
        """
        Load a trained model
        
        Args:
            model_id: Model identifier
        
        Returns:
            Loaded model
        """
        model_path = self.models_dir / f"{model_id}.joblib"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model {model_id} not found")
        
        logger.info("Loading model", model_id=model_id)
        
        return joblib.load(model_path)
    
    def get_metadata(self, model_id: str) -> Optional[dict]:
        """
        Get model metadata
        
        Args:
            model_id: Model identifier
        
        Returns:
            Metadata dict or None
        """
        return self.model_metadata.get(model_id)


# Singleton instance
model_trainer = ModelTrainer()
