"""Caso de uso para obtener un incidente."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from src.domain.entities.incident import Incident
from src.domain.repositories import IIncidentRepository
from src.shared.logging import get_logger
from src.shared.exceptions import NotFoundException

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.get_incident")


class GetIncidentUseCase:
    """Caso de uso para obtener un incidente por ID."""

    def __init__(self, incident_repository: IIncidentRepository):
        self._incident_repo = incident_repository

    async def execute(self, incident_id: UUID) -> Optional[Incident]:
        """Ejecuta la obtención de un incidente."""
        logger.info(f"Getting incident", incident_id=str(incident_id))

        incident = await self._incident_repo.get_by_id(incident_id)

        if incident is None:
            logger.warning(f"Incident not found", incident_id=str(incident_id))
            raise NotFoundException("Incident", str(incident_id))

        logger.info(f"Incident retrieved", incident_id=str(incident_id))
        return incident
