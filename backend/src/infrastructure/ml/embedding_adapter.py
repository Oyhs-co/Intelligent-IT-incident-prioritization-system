"""Adapter para Sentence Transformers embeddings."""

from __future__ import annotations

from typing import Optional
import numpy as np

from src.application.ports import IEmbeddingModel
from src.shared.logging import get_logger

logger = get_logger("ml.embedding")

DEFAULT_MODEL = "all-MiniLM-L6-v2"


class SentenceTransformerEmbedding(IEmbeddingModel):
    """Implementación de embeddings usando Sentence Transformers."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "cpu",
        cache_folder: Optional[str] = None,
    ):
        self._model_name = model_name
        self._device = device
        self._cache_folder = cache_folder
        self._model = None
        self._dimension: Optional[int] = None

    def _load_model(self) -> None:
        """Carga el modelo de embeddings."""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                model_name_or_path=self._model_name,
                device=self._device,
                cache_folder=self._cache_folder,
            )
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(
                f"Embedding model loaded: {self._model_name}",
                dimension=self._dimension,
            )
        except ImportError:
            logger.warning("sentence-transformers not installed, using fallback")
            self._model = None
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self._model = None

    async def generate_embedding(self, text: str) -> list[float]:
        """Genera un embedding para el texto."""
        self._load_model()

        if self._model is None:
            return self._generate_fallback_embedding(text)

        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return self._generate_fallback_embedding(text)

    async def generate_batch(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings en lote."""
        self._load_model()

        if self._model is None:
            return [self._generate_fallback_embedding(t) for t in texts]

        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [self._generate_fallback_embedding(t) for t in texts]

    def get_dimension(self) -> int:
        """Retorna la dimensión de los embeddings."""
        self._load_model()
        if self._dimension:
            return self._dimension
        return 384

    def is_available(self) -> bool:
        """Verifica si el modelo está disponible."""
        self._load_model()
        return self._model is not None

    def _generate_fallback_embedding(self, text: str) -> list[float]:
        """Genera embedding simple basado en TF-IDF como fallback."""
        words = text.lower().split()
        dim = self.get_dimension()
        embedding = np.zeros(dim, dtype=np.float32)

        for i, word in enumerate(words[:dim]):
            embedding[i % dim] += hash(word) % 1000 / 1000.0

        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.tolist()


class TFIDFEmbedding(IEmbeddingModel):
    """Fallback usando TF-IDF simple."""

    def __init__(self, max_features: int = 500):
        self._max_features = max_features
        self._vocabulary: dict[str, int] = {}
        self._idf: Optional[np.ndarray] = None
        self._fitted = False

    def _tokenize(self, text: str) -> list[str]:
        """Tokeniza el texto."""
        return text.lower().split()

    def _fit(self, texts: list[str]) -> None:
        """Ajusta el modelo con textos de entrenamiento."""
        if self._fitted:
            return

        all_words = set()
        for text in texts:
            all_words.update(self._tokenize(text))

        self._vocabulary = {word: i for i, word in enumerate(list(all_words)[:self._max_features])}

        doc_freq = np.zeros(len(self._vocabulary))
        for text in texts:
            tokens = set(self._tokenize(text))
            for token in tokens:
                if token in self._vocabulary:
                    doc_freq[self._vocabulary[token]] += 1

        n_docs = len(texts)
        self._idf = np.log((n_docs + 1) / (doc_freq + 1)) + 1
        self._fitted = True

    async def generate_embedding(self, text: str) -> list[float]:
        """Genera embedding TF-IDF."""
        if not self._fitted:
            self._fit([text])

        dim = len(self._vocabulary)
        vector = np.zeros(dim, dtype=np.float32)
        tokens = self._tokenize(text)

        for token in tokens:
            if token in self._vocabulary:
                idx = self._vocabulary[token]
                vector[idx] += 1

        vector = vector * self._idf
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    async def generate_batch(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings en lote."""
        if not self._fitted:
            self._fit(texts)
        return [await self.generate_embedding(text) for text in texts]

    def get_dimension(self) -> int:
        """Retorna la dimensión de los embeddings."""
        return len(self._vocabulary) if self._vocabulary else self._max_features

    def is_available(self) -> bool:
        """Verifica si está disponible."""
        return True
