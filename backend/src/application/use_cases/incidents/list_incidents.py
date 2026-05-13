"""Caso de uso para listar incidentes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from src.domain.entities.incident import Incident
from src.domain.repositories import IIncidentRepository
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.list_incidents")


@dataclass
class ListIncidentsResult:
    """Resultado de listar incidentes."""

    items: list[Incident]
    total: int
    skip: int
    limit: int


class ListIncidentsUseCase:
    """Caso de uso para listar incidentes con filtros."""

    def __init__(self, incident_repository: IIncidentRepository):
        self._incident_repo = incident_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        priority: int | None = None,
        category: str | None = None,
        assigned_to: UUID | None = None,
        created_by: UUID | None = None,
        assigned_department: str | None = None,
    ) -> ListIncidentsResult:
        """Ejecuta el listado de incidentes."""
        logger.info(
            "Listing incidents",
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
        )

        incidents, total = await self._incident_repo.list_all(
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            category=category,
            assigned_to=assigned_to,
            created_by=created_by,
            assigned_department=assigned_department,
        )

        logger.info(
            "Incidents listed",
            total=total,
            returned=len(incidents),
        )

        return ListIncidentsResult(
            items=incidents,
            total=total,
            skip=skip,
            limit=limit,
        )
