"""
Interfaces abstractas para la pipeline de NLP (Principios SOLID).

Define contratos claros para:
- Codificación de texto (embeddings)
- Clasificación
- Almacenamiento/Recuperación de modelos

Esto permite intercambiar componentes sin modificar el código que los usa.
Principio: Dependency Inversion Principle (DIP)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import numpy as np


class IEncoder(ABC):
    """Interfaz para codificación de texto a features vectoriales."""
    
    @abstractmethod
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Convierte textos a vectores numéricos.
        
        Args:
            texts: Lista de textos a codificar
            batch_size: Tamaño del lote para procesamiento eficiente
            
        Returns:
            Matriz numpy de forma (n_texts, n_features)
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Retorna la dimensión del vector de salida."""
        pass
    
    @abstractmethod
    def save(self, path: Path) -> None:
        """Guarda el codificador en disco."""
        pass
    
    @classmethod
    @abstractmethod
    def load(cls, path: Path) -> 'IEncoder':
        """Carga un codificador desde disco."""
        pass


class IClassifier(ABC):
    """Interfaz para clasificación multiclase."""
    
    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Entrena el clasificador.
        
        Args:
            X: Matriz de features (n_samples, n_features)
            y: Vector de etiquetas (n_samples,)
        """
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predice etiquetas para nuevos datos.
        
        Args:
            X: Matriz de features (n_samples, n_features)
            
        Returns:
            Vector de predicciones (n_samples,)
        """
        pass
    
    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Retorna probabilidades por clase.
        
        Args:
            X: Matriz de features (n_samples, n_features)
            
        Returns:
            Matriz de probabilidades (n_samples, n_classes)
        """
        pass
    
    @abstractmethod
    def save(self, path: Path) -> None:
        """Guarda el modelo entrenado."""
        pass
    
    @abstractmethod
    def load(self, path: Path) -> None:
        """Carga un modelo entrenado."""
        pass
    
    @abstractmethod
    def get_feature_importance(self, X: np.ndarray, y: np.ndarray) -> Optional[np.ndarray]:
        """
        Retorna importancia de features (si aplica).
        
        Args:
            X: Features de entrenamiento
            y: Labels de entrenamiento
            
        Returns:
            Array de importancias o None si no aplica
        """
        pass