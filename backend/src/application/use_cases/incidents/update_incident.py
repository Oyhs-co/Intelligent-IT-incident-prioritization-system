"""Caso de uso para actualizar incidentes."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from uuid import UUID

from src.domain.entities.incident import Incident
from src.domain.entities.incident_event import IncidentEvent
from src.domain.repositories import IIncidentEventRepository, IIncidentRepository
from src.domain.value_objects import (
    EventType,
    IncidentCategory,
    IncidentStatus,
    PriorityLevel,
)
from src.shared.exceptions import NotFoundException
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.update_incident")


class UpdateIncidentUseCase:
    """Caso de uso para actualizar parcialmente un incidente."""

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
        title: str | None = None,
        description: str | None = None,
        category: str | None = None,
        subcategory: str | None = None,
        status: str | None = None,
        priority: int | None = None,
        urgency: int | None = None,
        impact: int | None = None,
        resolution: str | None = None,
        resolution_code: str | None = None,
        tags: list[str] | None = None,
        assigned_to: UUID | None = None,
        user_id: UUID | None = None,
    ) -> Incident:
        """Ejecuta la actualización parcial de un incidente."""
        start_time = time.time()

        logger.info("Updating incident", incident_id=str(incident_id))

        incident = await self._incident_repo.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident", str(incident_id))

        changes = {}

        if title is not None:
            old = incident.title
            incident.title = title
            if old != title:
                changes["title"] = (old, title)

        if description is not None:
            old = incident.description
            incident.description = description
            if old != description:
                changes["description"] = (old, description)

        if category is not None:
            old = incident.category.value if incident.category else None
            incident.category = IncidentCategory(category)
            if old != category:
                changes["category"] = (old, category)

        if subcategory is not None:
            old = incident.subcategory
            incident.subcategory = subcategory
            if old != subcategory:
                changes["subcategory"] = (old, subcategory)

        if status is not None:
            old = incident.status.value
            incident.status = IncidentStatus(status)
            if old != status:
                changes["status"] = (old, status)

        if priority is not None:
            old = incident.priority.value if incident.priority else None
            incident.priority = PriorityLevel.from_int(priority)
            if old != priority:
                changes["priority"] = (old, priority)

        if urgency is not None:
            old = incident.urgency
            incident.urgency = urgency
            if old != urgency:
                changes["urgency"] = (old, urgency)

        if impact is not None:
            old = incident.impact
            incident.impact = impact
            if old != impact:
                changes["impact"] = (old, impact)

        if resolution is not None:
            old_status = incident.status.value if incident.status else None
            if user_id is not None:
                incident.resolve(resolution, user_id, resolution_code)
            else:
                object.__setattr__(incident, "_resolution", resolution)
                if resolution_code is not None:
                    object.__setattr__(incident, "_resolution_code", resolution_code)
            changes["resolution"] = (incident.resolution, resolution)
            if resolution_code is not None:
                changes["resolution_code"] = (None, resolution_code)
            new_status = incident.status.value
            if old_status != new_status:
                changes["status"] = (old_status, new_status)
        else:
            if resolution_code is not None:
                old = incident.resolution_code
                incident.resolution_code = resolution_code
                if old != resolution_code:
                    changes["resolution_code"] = (old, resolution_code)

        if tags is not None:
            incident.tags = tags
            changes["tags"] = (None, tags)

        if assigned_to is not None:
            old = incident.assigned_to
            incident.assigned_to = assigned_to
            if old != assigned_to:
                changes["assigned_to"] = (str(old) if old else None, str(assigned_to))

        updated = await self._incident_repo.update(incident)

        if changes:
            event = IncidentEvent()
            event.incident_id = incident.id
            event.event_type = EventType.UPDATED
            event.user_id = user_id
            event.metadata = {"changes": list(changes.keys())}
            await self._event_repo.create(event)

        logger.log_execution_time(
            "update_incident",
            (time.time() - start_time) * 1000,
            incident_id=str(incident_id),
            changes=list(changes.keys()),
        )

        logger.info(
            "Incident updated successfully",
            incident_id=str(incident_id),
            changes=list(changes.keys()),
        )

        return updated
