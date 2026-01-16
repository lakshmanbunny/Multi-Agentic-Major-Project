"""
Optuna Hyperparameter Optimizer

Uses Optuna for automated hyperparameter optimization.
"""

import uuid
from typing import Dict, Optional

import optuna
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.svm import SVC

from core import setup_logger

logger = setup_logger("optuna_optimizer", level="INFO")


class OptunaOptimizer:
    """
    Hyperparameter optimization using Optuna
    
    Supports automatic hyperparameter search for various algorithms
    using Tree-structured Parzen Estimator (TPE) sampler.
    """
    
    def __init__(self, storage: Optional[str] = None):
        """
        Initialize optimizer
        
        Args:
            storage: Optuna storage URL (e.g., sqlite:///optuna.db)
        """
        self.storage = storage or "sqlite:///optuna.db"
        self.studies: Dict[str, optuna.Study] = {}
        
        logger.info("OptunaOptimizer initialized", storage=self.storage)
    
    async def optimize(
        self,
        dataset_path: str,
        target_column: str,
        algorithm: str = "RandomForestClassifier",
        n_trials: int = 100,
        timeout: Optional[int] = None,
        cv_folds: int = 5
    ) -> Dict:
        """
        Optimize hyperparameters
        
        Args:
            dataset_path: Path to dataset CSV
            target_column: Target column name
            algorithm: Algorithm to optimize
            n_trials: Number of optimization trials
            timeout: Timeout in seconds
            cv_folds: Number of cross-validation folds
        
        Returns:
            Dict with study_id, best_params, best_score
        """
        logger.info(
            "Starting hyperparameter optimization",
            algorithm=algorithm,
            n_trials=n_trials
        )
        
        try:
            # Load dataset
            df = pd.read_csv(dataset_path)
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Split for final evaluation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            logger.info("Dataset loaded", train_size=len(X_train))
            
            # Create study
            study_id = f"study-{uuid.uuid4().hex[:12]}"
            study = optuna.create_study(
                study_name=study_id,
                direction="maximize",
                storage=self.storage,
                load_if_exists=True,
                sampler=optuna.samplers.TPESampler()
            )
            
            # Define objective function
            def objective(trial):
                params = self._get_hyperparameter_space(trial, algorithm)
                
                # Create model with suggested parameters
                model = self._create_model(algorithm, params)
                
                # Cross-validation
                scores = cross_val_score(
                    model,
                    X_train,
                    y_train,
                    cv=cv_folds,
                    scoring="accuracy" if "Classifier" in algorithm else "r2"
                )
                
                return scores.mean()
            
            # Run optimization
            study.optimize(
                objective,
                n_trials=n_trials,
                timeout=timeout,
                show_progress_bar=False
            )
            
            # Store study
            self.studies[study_id] = study
            
            logger.info(
                "Optimization completed",
                study_id=study_id,
                best_score=study.best_value,
                n_trials=len(study.trials)
            )
            
            return {
                "study_id": study_id,
                "best_params": study.best_params,
                "best_score": study.best_value,
                "n_trials": len(study.trials),
                "algorithm": algorithm
            }
        
        except Exception as e:
            logger.error("Optimization failed", error=str(e), exc_info=True)
            raise
    
    def _get_hyperparameter_space(self, trial: optuna.Trial, algorithm: str) -> Dict:
        """
        Define hyperparameter search space for each algorithm
        
        Args:
            trial: Optuna trial object
            algorithm: Algorithm name
        
        Returns:
            Dict of hyperparameters
        """
        if algorithm == "RandomForestClassifier":
            return {
                "n_estimators": trial.suggest_int("n_estimators", 50, 500),
                "max_depth": trial.suggest_int("max_depth", 3, 20),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
                "max_features": trial.suggest_categorical(
                    "max_features", ["sqrt", "log2", None]
                ),
                "random_state": 42
            }
        
        elif algorithm == "LogisticRegression":
            return {
                "C": trial.suggest_float("C", 0.001, 100.0, log=True),
                "penalty": trial.suggest_categorical("penalty", ["l1", "l2", "elasticnet", None]),
                "solver": trial.suggest_categorical(
                    "solver", ["lbfgs", "liblinear", "saga"]
                ),
                "max_iter": trial.suggest_int("max_iter", 100, 1000),
                "random_state": 42
            }
        
        elif algorithm == "GradientBoostingClassifier":
            return {
                "n_estimators": trial.suggest_int("n_estimators", 50, 500),
                "learning_rate": trial.suggest_float("learning_rate", 0.001, 0.3, log=True),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "random_state": 42
            }
        
        elif algorithm == "SVC":
            return {
                "C": trial.suggest_float("C", 0.001, 100.0, log=True),
                "kernel": trial.suggest_categorical("kernel", ["linear", "rbf", "poly"]),
                "gamma": trial.suggest_categorical("gamma", ["scale", "auto"]),
                "random_state": 42
            }
        
        else:
            logger.warning(f"Unknown algorithm: {algorithm}, using default params")
            return {}
    
    def _create_model(self, algorithm: str, params: Dict):
        """
        Create model instance with parameters
        
        Args:
            algorithm: Algorithm name
            params: Hyperparameters
        
        Returns:
            Model instance
        """
        if algorithm == "RandomForestClassifier":
            return RandomForestClassifier(**params)
        elif algorithm == "LogisticRegression":
            return LogisticRegression(**params)
        elif algorithm == "GradientBoostingClassifier":
            return GradientBoostingClassifier(**params)
        elif algorithm == "SVC":
            return SVC(**params)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def get_study(self, study_id: str) -> Optional[optuna.Study]:
        """
        Get Optuna study by ID
        
        Args:
            study_id: Study identifier
        
        Returns:
            Study object or None
        """
        return self.studies.get(study_id)
    
    def get_study_stats(self, study_id: str) -> Optional[Dict]:
        """
        Get study statistics
        
        Args:
            study_id: Study identifier
        
        Returns:
            Dict with statistics or None
        """
        study = self.get_study(study_id)
        
        if not study:
            return None
        
        return {
            "study_id": study_id,
            "n_trials": len(study.trials),
            "best_value": study.best_value,
            "best_params": study.best_params,
            "best_trial": study.best_trial.number
        }


# Singleton instance
optuna_optimizer = OptunaOptimizer()
