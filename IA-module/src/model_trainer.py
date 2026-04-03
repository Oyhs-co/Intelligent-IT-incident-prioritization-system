"""
Entrenamiento y evaluación del modelo de priorización.

Incluye:
- Entrenamiento del modelo
- Validación
- Evaluación de desempeño
- Guardado/carga de modelos
"""

import pickle
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from .utils import logger, Config


class ModelTrainer:
    """Entrena y evalúa el modelo de priorización."""
    
    def __init__(self, random_state: int = Config.RANDOM_STATE):
        """
        Inicializa el entrenador.
        
        Args:
            random_state: Semilla para reproducibilidad
        """
        self.random_state = random_state
        self.model = None
        self.metrics = {}
    
    def create_model(self) -> LogisticRegression:
        """
        Crea una instancia del modelo Logistic Regression.
        
        Returns:
            Modelo configurado
        """
        logger.info("Creando modelo Logistic Regression")
        
        model = LogisticRegression(
            max_iter=1000,
            random_state=self.random_state,
            solver="lbfgs",
            class_weight="balanced"  # Para balancear clases
        )
        
        self.model = model
        return model
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray
    ) -> None:
        """
        Entrena el modelo.
        
        Args:
            X_train: Features de entrenamiento
            y_train: Labels de entrenamiento
        """
        if self.model is None:
            self.create_model()
        
        logger.info("Iniciando entrenamiento del modelo")
        self.model.fit(X_train, y_train)
        logger.info("Entrenamiento completado")
    
    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        dataset_name: str = "Validation"
    ) -> Dict[str, Any]:
        """
        Evalúa el modelo en un conjunto de datos.
        
        Args:
            X: Features
            y: Labels verdaderos
            dataset_name: Nombre del dataset para logging
            
        Returns:
            Diccionario con métricas
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        logger.info(f"Evaluando modelo en {dataset_name}")
        
        # Predicciones
        y_pred = self.model.predict(X)
        
        # Calcular métricas
        metrics = {
            "accuracy": accuracy_score(y, y_pred),
            "precision": precision_score(y, y_pred, average="weighted", zero_division=0),
            "recall": recall_score(y, y_pred, average="weighted", zero_division=0),
            "f1": f1_score(y, y_pred, average="weighted", zero_division=0),
            "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
            "classification_report": classification_report(y, y_pred, zero_division=0)
        }
        
        # Log de métricas
        logger.info(f"\n{dataset_name} Metrics:")
        logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['recall']:.4f}")
        logger.info(f"  F1-Score:  {metrics['f1']:.4f}")
        
        return metrics
    
    def validate(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> Dict[str, Any]:
        """
        Valida el modelo en el conjunto de validación.
        
        Args:
            X_val: Features de validación
            y_val: Labels de validación
            
        Returns:
            Métricas de validación
        """
        logger.info("\n" + "=" * 50)
        logger.info("VALIDACIÓN DEL MODELO")
        logger.info("=" * 50)
        
        val_metrics = self.evaluate(X_val, y_val, "Validation")
        
        # Verificar requisito mínimo RNF-08
        if val_metrics["accuracy"] < Config.MIN_ACCURACY:
            logger.warning(
                f"⚠ Accuracy ({val_metrics['accuracy']:.4f}) por debajo del mínimo "
                f"requerido ({Config.MIN_ACCURACY:.4f})"
            )
        else:
            logger.info(
                f"✓ Accuracy ({val_metrics['accuracy']:.4f}) cumple el requisito mínimo"
            )
        
        self.metrics["validation"] = val_metrics
        return val_metrics
    
    def test(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """
        Prueba el modelo en el conjunto de test.
        
        Args:
            X_test: Features de test
            y_test: Labels de test
            
        Returns:
            Métricas de test
        """
        logger.info("\n" + "=" * 50)
        logger.info("EVALUACIÓN EN TEST")
        logger.info("=" * 50)
        
        test_metrics = self.evaluate(X_test, y_test, "Test")
        
        # Verificar requisito mínimo
        if test_metrics["accuracy"] < Config.MIN_ACCURACY:
            logger.warning(
                f"⚠ Test Accuracy ({test_metrics['accuracy']:.4f}) por debajo "
                f"del mínimo requerido ({Config.MIN_ACCURACY:.4f})"
            )
        else:
            logger.info(
                f"✓ Test Accuracy ({test_metrics['accuracy']:.4f}) cumple el requisito"
            )
        
        self.metrics["test"] = test_metrics
        return test_metrics
    
    def save_model(self, model_path: Optional[Path] = None) -> None:
        """
        Guarda el modelo entrenado.
        
        Args:
            model_path: Ruta donde guardar (usa default si no se especifica)
        """
        if self.model is None:
            raise ValueError("No hay modelo entrenado para guardar")
        
        save_path = model_path or Config.MODEL_FILE
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, "wb") as f:
            pickle.dump(self.model, f)
        
        logger.info(f"Modelo guardado en {save_path}")
    
    def load_model(self, model_path: Optional[Path] = None) -> None:
        """
        Carga un modelo entrenado.
        
        Args:
            model_path: Ruta del modelo (usa default si no se especifica)
        """
        load_path = model_path or Config.MODEL_FILE
        
        if not load_path.exists():
            raise FileNotFoundError(f"Archivo de modelo no encontrado: {load_path}")
        
        with open(load_path, "rb") as f:
            self.model = pickle.load(f)
        
        logger.info(f"Modelo cargado desde {load_path}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Realiza predicciones.
        
        Args:
            X: Features
            
        Returns:
            Array de predicciones
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Retorna probabilidades de predicción.
        
        Args:
            X: Features
            
        Returns:
            Matriz de probabilidades
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        return self.model.predict_proba(X)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Retorna un resumen de todas las métricas.
        
        Returns:
            Diccionario con resumen de métricas
        """
        return self.metrics
    
    def print_summary(self) -> None:
        """Imprime un resumen del entrenamiento."""
        logger.info("\n" + "=" * 50)
        logger.info("RESUMEN DEL ENTRENAMIENTO")
        logger.info("=" * 50)
        
        if "validation" in self.metrics:
            logger.info("\nValidation Metrics:")
            for key, value in self.metrics["validation"].items():
                if key not in ["confusion_matrix", "classification_report"]:
                    logger.info(f"  {key}: {value:.4f}")
        
        if "test" in self.metrics:
            logger.info("\nTest Metrics:")
            for key, value in self.metrics["test"].items():
                if key not in ["confusion_matrix", "classification_report"]:
                    logger.info(f"  {key}: {value:.4f}")
        
        logger.info("=" * 50 + "\n")
