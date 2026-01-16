"""
Model Evaluator

Provides detailed model evaluation and metrics.
"""

from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from core import setup_logger

logger = setup_logger("model_evaluator", level="INFO")


class ModelEvaluator:
    """
    Evaluate trained models with comprehensive metrics
    
    Provides detailed evaluation including confusion matrices,
    classification reports, and feature importance (when available).
    """
    
    def __init__(self):
        """Initialize evaluator"""
        logger.info("ModelEvaluator initialized")
    
    async def evaluate(self, model_id: str) -> Dict:
        """
        Evaluate a trained model
        
        Args:
            model_id: Model identifier
        
        Returns:
            Dict with comprehensive evaluation metrics
        """
        logger.info("Evaluating model", model_id=model_id)
        
        try:
            # Load model from trainer
            from .trainer import model_trainer
            
            model = model_trainer.load_model(model_id)
            metadata = model_trainer.get_metadata(model_id)
            
            if not metadata:
                raise ValueError(f"Model {model_id} not found in metadata")
            
            # Load dataset
            dataset_path = metadata["dataset_path"]
            target_column = metadata["target_column"]
            test_size = metadata.get("test_size", 0.2)
            random_state = metadata.get("random_state", 42)
            
            df = pd.read_csv(dataset_path)
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Split data (same as training)
            from sklearn.model_selection import train_test_split
            
            _, X_test, _, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            algorithm = metadata["algorithm"]
            is_classification = "Classifier" in algorithm or "SVC" in algorithm
            
            metrics = {}
            
            if is_classification:
                # Classification metrics
                metrics["accuracy"] = float(accuracy_score(y_test, y_pred))
                
                # Confusion matrix
                cm = confusion_matrix(y_test, y_pred)
                
                # Classification report
                report = classification_report(y_test, y_pred)
                
                # Per-class metrics
                report_dict = classification_report(y_test, y_pred, output_dict=True)
                metrics["precision"] = float(report_dict["weighted avg"]["precision"])
                metrics["recall"] = float(report_dict["weighted avg"]["recall"])
                metrics["f1_score"] = float(report_dict["weighted avg"]["f1-score"])
                
                result = {
                    "metrics": metrics,
                    "confusion_matrix": cm.tolist(),
                    "classification_report": report
                }
            
            else:
                # Regression metrics
                metrics["mse"] = float(mean_squared_error(y_test, y_pred))
                metrics["rmse"] = float(np.sqrt(metrics["mse"]))
                metrics["mae"] = float(mean_absolute_error(y_test, y_pred))
                metrics["r2_score"] = float(r2_score(y_test, y_pred))
                
                result = {
                    "metrics": metrics,
                    "confusion_matrix": [],
                    "classification_report": ""
                }
            
            # Feature importance (if available)
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                feature_names = X.columns.tolist()
                
                feature_importance = {
                    name: float(importance)
                    for name, importance in zip(feature_names, importances)
                }
                
                # Sort by importance
                feature_importance = dict(
                    sorted(
                        feature_importance.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]  # Top 10 features
                )
                
                result["feature_importance"] = feature_importance
            
            logger.info(
                "Model evaluated",
                model_id=model_id,
                accuracy=metrics.get("accuracy", metrics.get("r2_score", 0.0))
            )
            
            return result
        
        except Exception as e:
            logger.error("Evaluation failed", error=str(e), exc_info=True)
            raise
    
    def compare_models(self, model_ids: List[str]) -> Dict:
        """
        Compare multiple models
        
        Args:
            model_ids: List of model identifiers
        
        Returns:
            Comparison results
        """
        logger.info("Comparing models", count=len(model_ids))
        
        from .trainer import model_trainer
        
        comparisons = []
        
        for model_id in model_ids:
            metadata = model_trainer.get_metadata(model_id)
            
            if metadata:
                comparisons.append({
                    "model_id": model_id,
                    "algorithm": metadata["algorithm"],
                    "metrics": metadata["metrics"],
                    "created_at": metadata["created_at"],
                    "training_time": metadata["training_time"]
                })
        
        # Sort by primary metric (accuracy or r2_score)
        comparisons.sort(
            key=lambda x: x["metrics"].get(
                "accuracy",
                x["metrics"].get("r2_score", 0.0)
            ),
            reverse=True
        )
        
        return {
            "count": len(comparisons),
            "models": comparisons
        }


# Singleton instance
model_evaluator = ModelEvaluator()
