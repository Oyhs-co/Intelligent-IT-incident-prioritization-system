"""Puerto para canales de notificación."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class INotificationChannel(ABC):
    """Interfaz abstracta para canales de notificación."""

    @abstractmethod
    async def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Envía una notificación.

        Args:
            recipient: Destinatario
            subject: Asunto
            message: Mensaje
            metadata: Metadatos adicionales

        Returns:
            True si se envió correctamente
        """
        raise NotImplementedError

    @abstractmethod
    def supports_channel(self, channel_type: str) -> bool:
        """
        Verifica si soporta el tipo de canal.

        Args:
            channel_type: Tipo de canal (email, slack, sms, etc.)

        Returns:
            True si lo soporta
        """
        raise NotImplementedError

    @abstractmethod
    def get_channel_name(self) -> str:
        """Retorna el nombre del canal."""
        raise NotImplementedError
