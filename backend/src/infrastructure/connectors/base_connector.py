"""Conector base para sistemas de tickets."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum

from src.shared.logging import get_logger

logger = get_logger("connectors.base")


class TicketConnectionError(Exception):
    """Error de conexión con el sistema de tickets."""
    pass


class TicketSyncError(Exception):
    """Error de sincronización con el sistema de tickets."""
    pass


class SyncDirection(str, Enum):
    """Dirección de sincronización."""
    PULL = "pull"
    PUSH = "push"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class ExternalTicket:
    """Representación de un ticket externo."""

    external_id: str
    external_system: str
    title: str
    description: str
    status: str
    priority: Optional[int] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class BaseTicketConnector(ABC):
    """Clase base para conectores de sistemas de tickets."""

    def __init__(
        self,
        base_url: str,
        api_token: str,
        username: Optional[str] = None,
        timeout: int = 30,
    ):
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._username = username
        self._timeout = timeout
        self._connected = False

    @abstractmethod
    async def connect(self) -> bool:
        """Establece conexión con el sistema."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Cierra la conexión."""
        raise NotImplementedError

    @abstractmethod
    async def get_ticket(self, ticket_id: str) -> ExternalTicket:
        """Obtiene un ticket por su ID."""
        raise NotImplementedError

    @abstractmethod
    async def list_tickets(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ExternalTicket]:
        """Lista tickets del sistema."""
        raise NotImplementedError

    @abstractmethod
    async def create_ticket(
        self,
        title: str,
        description: str,
        priority: Optional[int] = None,
        category: Optional[str] = None,
        **kwargs,
    ) -> ExternalTicket:
        """Crea un nuevo ticket."""
        raise NotImplementedError

    @abstractmethod
    async def update_ticket(
        self,
        ticket_id: str,
        **updates,
    ) -> ExternalTicket:
        """Actualiza un ticket existente."""
        raise NotImplementedError

    @abstractmethod
    async def sync_ticket(
        self,
        internal_incident_id: str,
        external_ticket_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
    ) -> dict[str, Any]:
        """Sincroniza un ticket entre sistemas."""
        raise NotImplementedError

    def is_connected(self) -> bool:
        """Verifica si está conectado."""
        return self._connected

    async def health_check(self) -> dict[str, Any]:
        """Verifica el estado de la conexión."""
        try:
            await self.connect()
            return {
                "status": "healthy",
                "connected": self._connected,
                "system": self.__class__.__name__,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "system": self.__class__.__name__,
            }
