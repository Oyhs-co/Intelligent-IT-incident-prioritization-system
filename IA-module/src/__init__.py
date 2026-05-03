"""
Paquete principal del Sistema de Priorización de Incidentes IT.

Incluye módulos:
- data_processor: Procesamiento y limpieza de datos
- encoders: Codificación de texto (MiniLM, TF-IDF)
- classifiers: Modelos de clasificación (LightGBM, Ensamble)
- model_trainer: Entrenamiento y evaluación
- predictor: Predicción y explicabilidad
- interfaces: Contratos abstractos (SOLID)
- utils: Configuración y logging
"""

__version__ = "2.0.0"
__author__ = "Jesus-MMM"

# Exponer interfaces y clases principales
from .interfaces import IEncoder, IClassifier
from .encoders import MiniLMEncoder, TFIDFEncoder
from .classifiers import LightGBMClassifier, FallbackEnsembleClassifier
from .model_trainer import ModelTrainer, ModelFactory
from .predictor import PriorityPredictor, save_model_artifacts, load_model_artifacts
from .utils import Config

__all__ = [
    "IEncoder",
    "IClassifier",
    "MiniLMEncoder",
    "TFIDFEncoder",
    "LightGBMClassifier",
    "FallbackEnsembleClassifier",
    "ModelTrainer",
    "ModelFactory",
    "PriorityPredictor",
    "save_model_artifacts",
    "load_model_artifacts",
    "Config"
]
