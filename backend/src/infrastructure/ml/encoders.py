import pickle
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from ._utils import logger
from .interfaces import IEncoder


class MiniLMEncoder(IEncoder):
    MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(self, model_name: str = MODEL_NAME):
        logger.info(f"Cargando modelo MiniLM: {model_name}")
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_embedding_dimension()
        logger.info(f"Modelo cargado. Dimensión: {self._dimension}")

    def encode(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        if not texts:
            return np.array([]).reshape(0, self._dimension)

        logger.info(f"Codificando {len(texts)} textos (batch_size={batch_size})...")

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            device="cpu",
            normalize_embeddings=True
        )

        embeddings = embeddings.astype(np.float32)
        logger.info(f"Codificación completada. Shape: {embeddings.shape}")

        return embeddings

    def get_dimension(self) -> int:
        return self._dimension

    def save(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self.model.save(str(path))
        logger.info(f"Encoder guardado en {path}")

    @classmethod
    def load(cls, path: Path) -> 'MiniLMEncoder':
        instance = cls.__new__(cls)
        instance.model = SentenceTransformer(str(path))
        instance._dimension = instance.model.get_embedding_dimension()
        logger.info(f"Encoder cargado desde {path}")
        return instance


class TFIDFEncoder(IEncoder):
    def __init__(self, max_features: int = 1000, min_df: int = 1, max_df: float = 1.0):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=(1, 2),
            lowercase=True
        )
        self._fitted = False

    def encode(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        if self._fitted:
            X = self.vectorizer.transform(texts)
        else:
            X = self.vectorizer.fit_transform(texts)
            self._fitted = True
        return X.toarray().astype(np.float32)

    def get_dimension(self) -> int:
        if not self._fitted:
            raise ValueError("Encoder no entrenado aún")
        return len(self.vectorizer.get_feature_names_out())

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        logger.info(f"TF-IDF guardado en {path}")

    @classmethod
    def load(cls, path: Path) -> 'TFIDFEncoder':
        instance = cls.__new__(cls)
        with open(path, 'rb') as f:
            instance.vectorizer = pickle.load(f)
        instance._fitted = True
        logger.info(f"TF-IDF cargado desde {path}")
        return instance
