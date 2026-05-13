"""Adapters that wrap MiniLMEncoder/TFIDFEncoder to implement IEmbeddingModel.

Replaces the previous SentenceTransformerEmbedding and TFIDFEmbedding
that had their own duplicate implementations. Now delegates to the
canonical encoders from encoders.py to avoid double model loading.
"""

from __future__ import annotations

from src.application.ports import IEmbeddingModel
from src.infrastructure.ml.encoders import MiniLMEncoder, TFIDFEncoder
from src.shared.logging import get_logger

logger = get_logger("ml.embedding_adapter")


class MiniLMEmbeddingAdapter(IEmbeddingModel):
    """Adapts MiniLMEncoder to the IEmbeddingModel interface.

    Eliminates duplication by delegating to MiniLMEncoder (the canonical
    implementation) instead of loading sentence-transformers separately.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        cache_folder: str | None = None,
    ):
        self._encoder = MiniLMEncoder(model_name=model_name)
        self._device = device
        self._cache_folder = cache_folder

    async def generate_embedding(self, text: str) -> list[float]:
        embedding = self._encoder.encode([text])
        return embedding[0].tolist()

    async def generate_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._encoder.encode(texts)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        return self._encoder.get_dimension()

    def is_available(self) -> bool:
        return True


class TFIDFEmbeddingAdapter(IEmbeddingModel):
    """Adapts TFIDFEncoder to the IEmbeddingModel interface."""

    def __init__(self, max_features: int = 1000):
        self._encoder = TFIDFEncoder(max_features=max_features)

    async def generate_embedding(self, text: str) -> list[float]:
        embedding = self._encoder.encode([text])
        return embedding[0].tolist()

    async def generate_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._encoder.encode(texts)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        return self._encoder.get_dimension()

    def is_available(self) -> bool:
        return True
