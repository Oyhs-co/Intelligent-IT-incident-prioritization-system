"""Puerto para modelos de IA."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IAIModel(ABC):
    """Interfaz abstracta para modelos de IA."""

    @abstractmethod
    async def predict(self, text: str) -> tuple[int, float]:
        """
        Predice la prioridad de un texto.

        Args:
            text: Texto del incidente

        Returns:
            Tupla (prioridad, confianza)
        """
        raise NotImplementedError

    @abstractmethod
    async def predict_with_explanation(self, text: str) -> dict[str, Any]:
        """
        Predice con explicación detallada.

        Args:
            text: Texto del incidente

        Returns:
            Diccionario con predicción y features
        """
        raise NotImplementedError

    @abstractmethod
    async def batch_predict(self, texts: list[str]) -> list[tuple[int, float]]:
        """
        Predice en lote.

        Args:
            texts: Lista de textos

        Returns:
            Lista de tuplas (prioridad, confianza)
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el modelo está disponible."""
        raise NotImplementedError
