"""
Entrenamiento y evaluación del modelo de priorización.

Incluye:
- Entrenamiento del modelo (LightGBM / TF-IDF + LR)
- Validación
- Evaluación de desempeño
- Guardado/carga de modelos

Principio OCP: Extensible sin modificar código existente.
Principio DIP: Depende de IClassifier e IEncoder abstracciones.
"""

import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from .classifiers import FallbackEnsembleClassifier, LightGBMClassifier
from .encoders import MiniLMEncoder, TFIDFEncoder
from .interfaces import IClassifier, IEncoder
from .utils import logger, Config


class ModelTrainer:
    """Entrena y evalúa el modelo de priorización.
    
    Usa inyección de dependencias para clasificador y encoder.
    Soporta múltiples backends intercambiables.
    """
    
    def __init__(
        self,
        classifier: Optional[IClassifier] = None,
        encoder: Optional[IEncoder] = None,
        random_state: int = Config.RANDOM_STATE
    ):
        """
        Inicializa el entrenador.
        
        Args:
            classifier: Clasificador a usar. Si None, crea uno por defecto.
            encoder: Encoder para guardar/guardar artefactos.
            random_state: Semilla para reproducibilidad.
        """
        self.random_state = random_state
        self.classifier = classifier
        self.encoder = encoder
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def create_model(self, n_classes: int = 3) -> IClassifier:
        """
        Crea un clasificador por defecto (LightGBM).
        
        Args:
            n_classes: Número de clases (default: 3 para P1/P2/P3)
            
        Returns:
            Clasificador configurado
        """
        logger.info("Creando modelo LightGBM classifier (por defecto)")
        
        model = ModelFactory.create_lightgbm(
            n_classes=n_classes,
            num_leaves=Config.LGB_NUM_LEAVES,
            max_depth=Config.LGB_MAX_DEPTH,
            learning_rate=Config.LGB_LEARNING_RATE
        )
        
        self.classifier = model
        return model
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> None:
        """
        Entrena el modelo.
        
        Args:
            X_train: Features de entrenamiento
            y_train: Labels de entrenamiento
            X_val: Features de validación (opcional, para early stopping)
            y_val: Labels de validación (opcional)
        """
        if self.classifier is None:
            self.create_model()
        
        logger.info("Iniciando entrenamiento del modelo")
        logger.info(f"  Train samples: {X_train.shape[0]}")
        logger.info(f"  Features: {X_train.shape[1]}")
        logger.info(f"  Classes: {len(np.unique(y_train))}")
        
        self.classifier.fit(X_train, y_train)
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
            y: Labels verdaderos (0-index: 0=P1, 1=P2, 2=P3)
            dataset_name: Nombre del dataset para logging
            
        Returns:
            Diccionario con métricas
        """
        if self.classifier is None:
            raise ValueError("Modelo no entrenado")
        
        logger.info(f"Evaluando modelo en {dataset_name}")
        
        # Predicciones
        y_pred = self.classifier.predict(X)
        y_pred_labels = y_pred + 1  # Convertir de 0-index a 1-3
        y_true_labels = y + 1
        
        # Probabilidades
        y_proba = self.classifier.predict_proba(X)
        
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
        
        # Matriz de confusión
        cm = metrics["confusion_matrix"]
        logger.info(f"\n  Confusion Matrix:")
        logger.info(f"    Predicted ->")
        logger.info(f"       P1  P2  P3")
        for i, row in enumerate(cm):
            logger.info(f"  P{i+1}  {row[0]:3d} {row[1]:3d} {row[2]:3d}")
        
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
        logger.info("\n" + "=" * 60)
        logger.info("VALIDACIÓN DEL MODELO")
        logger.info("=" * 60)
        
        val_metrics = self.evaluate(X_val, y_val, "Validation")
        
        # Verificar requisito mínimo RNF-08 (accuracy >= 0.70)
        if val_metrics["accuracy"] < Config.MIN_ACCURACY:
            logger.warning(
                f"[WARN] Accuracy ({val_metrics['accuracy']:.4f}) por debajo del mínimo "
                f"requerido ({Config.MIN_ACCURACY:.4f})"
            )
        else:
            logger.info(
                f"[OK] RNF-08: Accuracy ({val_metrics['accuracy']:.4f}) cumple requisito mínimo"
            )
        
        # Meta aspiracional: accuracy >= 0.85 con MiniLM + LightGBM
        if val_metrics["accuracy"] >= 0.85:
            logger.info(
                f"[OK] Excelente: Accuracy ({val_metrics['accuracy']:.4f}) >= 85% (Meta aspiracional)"
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
        logger.info("\n" + "=" * 60)
        logger.info("EVALUACIÓN EN TEST")
        logger.info("=" * 60)
        
        test_metrics = self.evaluate(X_test, y_test, "Test")
        
        # Verificar requisito mínimo RNF-08
        if test_metrics["accuracy"] < Config.MIN_ACCURACY:
            logger.warning(
                f"⚠ Test Accuracy ({test_metrics['accuracy']:.4f}) por debajo "
                f"del mínimo requerido ({Config.MIN_ACCURACY:.4f})"
            )
        else:
            logger.info(
                f"[OK] RNF-08: Test Accuracy ({test_metrics['accuracy']:.4f}) cumple requisito"
            )
        
        # Verificar RNF-10 (capacidad de generalización)
        train_val_gap = None
        if "validation" in self.metrics:
            train_val_gap = abs(self.metrics["validation"]["accuracy"] - test_metrics["accuracy"])
            logger.info(f"\n  Gap validation-test: {train_val_gap:.4f}")
            if train_val_gap < 0.05:
                logger.info(f"[OK] RNF-10: Buena capacidad de generalización (gap < 5%)")
            else:
                logger.warning(f"[WARN] RNF-10: Posible overfitting (gap > 5%)")
        
        self.metrics["test"] = test_metrics
        return test_metrics
    
    def save_model(
        self,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Guarda el modelo entrenado y artefactos.
        
        Args:
            model_path: Ruta donde guardar el modelo
            encoder_path: Ruta donde guardar el encoder
            metadata: Metadatos adicionales (métricas, parámetros, etc.)
        """
        if self.classifier is None:
            raise ValueError("No hay modelo entrenado para guardar")
        
        # Guardar modelo clasificador
        save_path = model_path or Config.MODEL_FILE
        save_path.parent.mkdir(parents=True, exist_ok=True)
        self.classifier.save(save_path)
        logger.info(f"Modelo guardado en {save_path}")
        
        # Guardar encoder si está disponible
        if self.encoder is not None:
            vec_path = encoder_path or Config.ENCODER_DIR
            self.encoder.save(vec_path)
            logger.info(f"Encoder guardado en {vec_path}")
        
        # Guardar metadata
        if metadata is None:
            metadata = {
                "metrics": self.metrics,
                "classifier_params": self.classifier.get_params() if hasattr(self.classifier, 'get_params') else None,
                "random_state": self.random_state
            }
        
        metadata_path = save_path.parent / "metadata.json"
        with open(metadata_path, 'w') as f:
            # Convertir numpy types a Python types para JSON
            def default_serializer(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                raise TypeError(f"Type {type(obj)} not serializable")
            
            json.dump(metadata, f, indent=2, default=default_serializer)
        logger.info(f"Metadata guardada en {metadata_path}")
    
    def load_model(
        self,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None
    ) -> None:
        """
        Carga un modelo entrenado y encoder.
        
        Args:
            model_path: Ruta del modelo
            encoder_path: Ruta del encoder
        """
        load_path = model_path or Config.MODEL_FILE
        
        if not load_path.exists():
            raise FileNotFoundError(f"Archivo de modelo no encontrado: {load_path}")
        
        # Intentar cargar como LightGBM primero
        try:
            self.classifier = LightGBMClassifier()
            self.classifier.load(load_path)
            logger.info(f"Modelo LightGBM cargado desde {load_path}")
        except Exception:
            # Fallback a LogisticRegression
            with open(load_path, 'rb') as f:
                self.classifier = pickle.load(f)
            logger.info(f"Modelo LogisticRegression cargado desde {load_path}")
        
        # Cargar encoder si se especifica
        if encoder_path is not None:
            self._load_encoder(encoder_path)
    
    def _load_encoder(self, encoder_path: Path) -> None:
        """Carga encoder desde disco."""
        
        # Intenta MiniLM primero
        try:
            self.encoder = MiniLMEncoder.load(encoder_path)
            logger.info(f"Encoder MiniLM cargado desde {encoder_path}")
        except Exception:
            # Fallback a TF-IDF
            try:
                self.encoder = TFIDFEncoder.load(encoder_path)
                logger.info(f"Encoder TF-IDF cargado desde {encoder_path}")
            except Exception:
                logger.warning(f"No se pudo cargar encoder desde {encoder_path}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Realiza predicciones.
        
        Args:
            X: Features (0-index)
            
        Returns:
            Predicciones (0-index: 0=P1, 1=P2, 2=P3)
        """
        if self.classifier is None:
            raise ValueError("Modelo no entrenado")
        
        return self.classifier.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Retorna probabilidades de predicción.
        
        Args:
            X: Features
            
        Returns:
            Matriz de probabilidades (n_samples, n_classes)
        """
        if self.classifier is None:
            raise ValueError("Modelo no entrenado")
        
        return self.classifier.predict_proba(X)
    
    def predict_with_labels(self, X: np.ndarray) -> np.ndarray:
        """
        Realiza predicciones con labels 1-3.
        
        Args:
            X: Features
            
        Returns:
            Predicciones (1-index: 1=P1, 2=P2, 3=P3)
        """
        predictions = self.predict(X)
        return predictions + 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna un resumen de todas las métricas."""
        return self.metrics
    
    def print_summary(self) -> None:
        """Imprime un resumen del entrenamiento."""
        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN DEL ENTRENAMIENTO")
        logger.info("=" * 60)
        
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
        
        logger.info("=" * 60 + "\n")


class ModelFactory:
    """
    Factoría para crear modelos según configuración.
    
    Facilita la creación de diferentes configuraciones
    sin exponer la lógica de instanciación.
    """
    
    @staticmethod
    def create_lightgbm(
        n_classes: int = 3,
        num_leaves: int = 31,
        max_depth: int = 6,
        learning_rate: float = 0.05
    ) -> IClassifier:
        """Crea un clasificador LightGBM."""
        return LightGBMClassifier(
            n_classes=n_classes,
            num_leaves=num_leaves,
            max_depth=max_depth,
            learning_rate=learning_rate,
            n_estimators=Config.LGB_N_ESTIMATORS,
            min_child_samples=20,
            reg_alpha=0.0,
            reg_lambda=0.0,
            random_state=Config.RANDOM_STATE,
            verbose=-1
        )
    
    @staticmethod
    def create_ensemble() -> IClassifier:
        """Crea un ensamble LightGBM + LogisticRegression."""
        return FallbackEnsembleClassifier(lgb_weight=0.6)
    
    @staticmethod
    def create_minilm_encoder() -> IEncoder:
        """Crea un encoder MiniLM."""
        return MiniLMEncoder()
    
    @staticmethod
    def create_tfidf_encoder(max_features: int = 1000) -> IEncoder:
        """Crea un encoder TF-IDF."""
        return TFIDFEncoder(max_features=max_features)

