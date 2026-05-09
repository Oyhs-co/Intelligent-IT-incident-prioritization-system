"""ML infrastructure: encoders, classifiers, training, prediction, and vector store."""

from ._utils import Config
from .classifiers import FallbackEnsembleClassifier, LightGBMClassifier
from .embedding_adapter import MiniLMEmbeddingAdapter, TFIDFEmbeddingAdapter
from .encoders import MiniLMEncoder, TFIDFEncoder
from .interfaces import IClassifier, IEncoder
from .model_trainer import ModelFactory, ModelTrainer
from .predictor import PriorityPredictor, load_model_artifacts, save_model_artifacts
from .vector_store import IncidentVectorStore

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
    "Config",
    "MiniLMEmbeddingAdapter",
    "TFIDFEmbeddingAdapter",
    "IncidentVectorStore",
]
