"""Caso de uso para crear incidentes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from uuid import UUID
import time

from src.domain.entities.incident import Incident
from src.domain.entities.incident_event import IncidentEvent
from src.domain.repositories import IIncidentRepository, IIncidentEventRepository
from src.domain.value_objects import IncidentCategory, IncidentSource, IncidentStatus, PriorityLevel, EventType
from src.application.services import AIService
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.create_incident")


@dataclass
class CreateIncidentRequest:
    """Request para crear un incidente."""

    title: str
    description: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    urgency: int = 3
    impact: int = 3
    source: str = "web"


class CreateIncidentUseCase:
    """Caso de uso para crear un nuevo incidente."""

    def __init__(
        self,
        incident_repository: IIncidentRepository,
        event_repository: IIncidentEventRepository,
        ai_service: AIService,
    ):
        self._incident_repo = incident_repository
        self._event_repo = event_repository
        self._ai_service = ai_service

    async def execute(
        self,
        request: CreateIncidentRequest,
        user_id: Optional[UUID] = None,
    ) -> Incident:
        """Ejecuta la creación de un incidente."""
        start_time = time.time()

        logger.info(
            f"Creating new incident",
            title=request.title[:50],
            category=request.category,
        )

        incident = Incident()
        incident.title = request.title
        incident.description = request.description
        incident.urgency = request.urgency
        incident.impact = request.impact

        if request.category:
            incident.category = IncidentCategory(request.category)

        incident.subcategory = request.subcategory
        incident.source = IncidentSource(request.source)
        incident.reporter_id = user_id
        incident.status = IncidentStatus.NEW

        ticket_number = await self._incident_repo.get_next_ticket_number()
        incident.ticket_number = ticket_number

        saved_incident = await self._incident_repo.create(incident)

        event = IncidentEvent()
        event.incident_id = saved_incident.id
        event.event_type = EventType.CREATED
        event.user_id = user_id
        event.metadata = {
            "ticket_number": ticket_number,
            "source": request.source,
        }
        await self._event_repo.create(event)

        logger.log_execution_time(
            "create_incident",
            (time.time() - start_time) * 1000,
            incident_id=str(saved_incident.id),
            ticket_number=ticket_number,
        )

        logger.info(
            f"Incident created successfully",
            incident_id=str(saved_incident.id),
            ticket_number=ticket_number,
        )

        return saved_incident
