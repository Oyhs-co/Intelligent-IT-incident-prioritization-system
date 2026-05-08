"""Interfaces de repositorios."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

from ..entities.comment import Comment
from ..entities.incident import Incident
from ..entities.incident_event import IncidentEvent
from ..entities.user import User


class IIncidentRepository(ABC):
    """Interfaz abstracta para el repositorio de incidentes."""

    @abstractmethod
    async def create(self, incident: Incident) -> Incident:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, incident_id: UUID) -> Incident | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ticket_number(self, ticket_number: str) -> Incident | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, incident: Incident) -> Incident:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, incident_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        priority: int | None = None,
        category: str | None = None,
        assigned_to: UUID | None = None,
        created_by: UUID | None = None,
    ) -> tuple[list[Incident], int]:
        raise NotImplementedError

    @abstractmethod
    async def get_next_ticket_number(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def count_by_status(self) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    async def count_by_priority(self) -> dict[int, int]:
        raise NotImplementedError

    @abstractmethod
    async def count_by_category(self) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    async def sla_breach_count(self) -> int:
        raise NotImplementedError


class IUserRepository(ABC):
    """Interfaz abstracta para el repositorio de usuarios."""

    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        raise NotImplementedError


class ICommentRepository(ABC):
    """Interfaz abstracta para el repositorio de comentarios."""

    @abstractmethod
    async def create(self, comment: Comment) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, comment: Comment) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, comment_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_by_incident(
        self,
        incident_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_internal: bool = False,
    ) -> tuple[list[Comment], int]:
        raise NotImplementedError


class IIncidentEventRepository(ABC):
    """Interfaz abstracta para el repositorio de eventos."""

    @abstractmethod
    async def create(self, event: IncidentEvent) -> IncidentEvent:
        raise NotImplementedError

    @abstractmethod
    async def list_by_incident(
        self,
        incident_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[IncidentEvent], int]:
        raise NotImplementedError
