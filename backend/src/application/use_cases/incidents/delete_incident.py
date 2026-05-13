"""Caso de uso para eliminar incidentes."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from uuid import UUID

from src.domain.entities.incident_event import IncidentEvent
from src.domain.repositories import IIncidentEventRepository, IIncidentRepository
from src.domain.value_objects import EventType
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.delete_incident")


class DeleteIncidentUseCase:
    """Caso de uso para eliminar un incidente."""

    def __init__(
        self,
        incident_repository: IIncidentRepository,
        event_repository: IIncidentEventRepository,
    ):
        self._incident_repo = incident_repository
        self._event_repo = event_repository

    async def execute(
        self,
        incident_id: UUID,
        user_id: UUID | None = None,
    ) -> bool:
        """Ejecuta la eliminación de un incidente.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        start_time = time.time()

        logger.info("Deleting incident", incident_id=str(incident_id))

        # First check the incident exists, then create event (FK constraint requires incident to exist)
        incident = await self._incident_repo.get_by_id(incident_id)
        if incident is None:
            return False

        event = IncidentEvent()
        event.incident_id = incident_id
        event.event_type = EventType.DELETED
        event.user_id = user_id
        await self._event_repo.create(event)

        deleted = await self._incident_repo.delete(incident_id)

        if deleted:
            logger.log_execution_time(
                "delete_incident",
                (time.time() - start_time) * 1000,
                incident_id=str(incident_id),
            )

            logger.info(
                "Incident deleted successfully",
                incident_id=str(incident_id),
            )

        return deleted
