"""
Codificador de texto usando MiniLM-L6-v2 (Sentence Transformers).

Optimizado para CPU con batch processing para no exceder RAM.
Proporciona embeddings densos de 384 dimensiones.
"""

import numpy as np
from pathlib import Path
from typing import List
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from .interfaces import IEncoder
from .utils import logger


class MiniLMEncoder(IEncoder):
    """Codificador MiniLM-L6-v2 para embeddings de texto."""
    
    MODEL_NAME = "all-MiniLM-L6-v2"
    
    def __init__(self, model_name: str = MODEL_NAME):
        """
        Inicializa el codificador.
        
        Args:
            model_name: Nombre del modelo en HuggingFace (default: all-MiniLM-L6-v2)
        """
        logger.info(f"Cargando modelo MiniLM: {model_name}")
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_embedding_dimension()
        logger.info(f"Modelo cargado. Dimensión: {self._dimension}")
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Codifica textos a embeddings de 384 dimensiones.
        
        Args:
            texts: Lista de textos (limpios)
            batch_size: Tamaño de lote (default: 32 para RAM <=8GB)
            
        Returns:
            Array numpy float32 de forma (len(texts), 384)
        """
        if not texts:
            return np.array([]).reshape(0, self._dimension)
        
        logger.info(f"Codificando {len(texts)} textos (batch_size={batch_size})...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            device="cpu",  # Fuerza CPU
            normalize_embeddings=True  # Normaliza para cosine similarity
        )
        
        # Asegura float32 para ahorrar RAM
        embeddings = embeddings.astype(np.float32)
        logger.info(f"Codificación completada. Shape: {embeddings.shape}")
        
        return embeddings
    
    def get_dimension(self) -> int:
        """Retorna dimensión del embedding (384 para MiniLM)."""
        return self._dimension
    
    def save(self, path: Path) -> None:
        """
        Guarda el modelo SentenceTransformer.
        
        Args:
            path: Directorio donde guardar
        """
        path.mkdir(parents=True, exist_ok=True)
        self.model.save(str(path))
        logger.info(f"Encoder guardado en {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'MiniLMEncoder':
        """
        Carga un encoder guardado.
        
        Args:
            path: Directorio del modelo guardado
            
        Returns:
            Instancia de MiniLMEncoder
        """
        instance = cls.__new__(cls)
        instance.model = SentenceTransformer(str(path))
        instance._dimension = instance.model.get_embedding_dimension()
        logger.info(f"Encoder cargado desde {path}")
        return instance


class TFIDFEncoder(IEncoder):
    """Encoder TF-IDF (fallback clásico)."""
    
    def __init__(self, max_features: int = 1000, min_df: int = 1, max_df: float = 1.0):
        """
        Args:
            max_features: Máximo de features TF-IDF
            min_df: Frecuencia mínima (int o float)
            max_df: Frecuencia máxima (int o float)
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=(1, 2),
            lowercase=True
        )
        self._fitted = False
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Codifica con TF-IDF (ignora batch_size).
        
        Args:
            texts: Lista de textos
            batch_size: Ignorado (compatibilidad con interfaz)
        """
        if self._fitted:
            X = self.vectorizer.transform(texts)
        else:
            X = self.vectorizer.fit_transform(texts)
            self._fitted = True
        return X.toarray().astype(np.float32)
    
    def get_dimension(self) -> int:
        """Dimensión del vocabulario TF-IDF."""
        if not self._fitted:
            raise ValueError("Encoder no entrenado aún")
        return len(self.vectorizer.get_feature_names_out())
    
    def save(self, path: Path) -> None:
        """Guarda vectorizador TF-IDF."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        logger.info(f"TF-IDF guardado en {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'TFIDFEncoder':
        """Carga vectorizador TF-IDF."""
        instance = cls.__new__(cls)
        with open(path, 'rb') as f:
            instance.vectorizer = pickle.load(f)
        instance._fitted = True
        logger.info(f"TF-IDF cargado desde {path}")
        return instance
