"""Puerto para embeddings."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IEmbeddingModel(ABC):
    """Interfaz abstracta para modelos de embeddings."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """
        Genera un embedding para el texto.

        Args:
            text: Texto a convertir

        Returns:
            Vector de embeddings
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Genera embeddings en lote.

        Args:
            texts: Lista de textos

        Returns:
            Lista de vectores de embeddings
        """
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self) -> int:
        """Retorna la dimensión de los embeddings."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el modelo está disponible."""
        raise NotImplementedError
