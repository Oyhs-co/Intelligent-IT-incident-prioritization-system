"""Puerto para clientes LLM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ILLMClient(ABC):
    """Interfaz abstracta para clientes LLM."""

    @abstractmethod
    async def generate_explanation(
        self,
        incident_data: dict[str, Any],
        similar_incidents: list[dict[str, Any]],
        priority: int,
        confidence: float,
    ) -> str:
        """
        Genera una explicación textual.

        Args:
            incident_data: Datos del incidente
            similar_incidents: Incidentes similares
            priority: Prioridad predicha
            confidence: Confianza de la predicción

        Returns:
            Explicación textual
        """
        raise NotImplementedError

    @abstractmethod
    async def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """
        Analiza el sentimiento del texto.

        Args:
            text: Texto a analizar

        Returns:
            Diccionario con análisis de sentimiento
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el cliente LLM está disponible."""
        raise NotImplementedError
