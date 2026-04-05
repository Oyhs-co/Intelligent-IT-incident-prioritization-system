"""Caso de uso para clasificar incidentes con IA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from uuid import UUID
import time

from src.domain.entities.incident import Incident
from src.domain.entities.incident_event import IncidentEvent
from src.domain.repositories import IIncidentRepository, IIncidentEventRepository
from src.domain.value_objects import PriorityLevel, EventType
from src.application.services import AIService
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.classify_incident")


@dataclass
class ClassificationResult:
    """Resultado de la clasificación."""

    incident_id: UUID
    priority: int
    priority_label: str
    confidence: float
    explanation: str
    top_features: list[str]
    processing_time_ms: float


class ClassifyIncidentUseCase:
    """Caso de uso para clasificar y priorizar un incidente."""

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
        incident_id: UUID,
        user_id: Optional[UUID] = None,
        force: bool = False,
    ) -> ClassificationResult:
        """Ejecuta la clasificación de un incidente."""
        start_time = time.time()

        logger.info(f"Classifying incident", incident_id=str(incident_id))

        incident = await self._incident_repo.get_by_id(incident_id)
        if incident is None:
            logger.warning(f"Incident not found", incident_id=str(incident_id))
            raise ValueError(f"Incident {incident_id} not found")

        if incident.priority is not None and not force:
            logger.info(
                f"Incident already classified, skipping",
                incident_id=str(incident_id),
                priority=incident.priority.value,
            )
            return ClassificationResult(
                incident_id=incident.id,
                priority=incident.priority.value,
                priority_label=incident.priority.label,
                confidence=incident.confidence_score or 0.0,
                explanation=incident.explanation or "",
                top_features=[],
                processing_time_ms=(time.time() - start_time) * 1000,
            )

        text = f"{incident.title} {incident.description}"

        prediction = await self._ai_service.predict_priority(text)

        priority_level = PriorityLevel.from_int(prediction.priority)

        incident.assign_priority(
            priority=priority_level,
            confidence=prediction.confidence,
            explanation=prediction.reasoning,
        )

        await self._incident_repo.update(incident)

        event = IncidentEvent()
        event.incident_id = incident.id
        event.event_type = EventType.PRIORITY_CHANGED
        event.old_value = str(incident.priority.value) if incident.priority else None
        event.new_value = str(prediction.priority)
        event.user_id = user_id
        event.metadata = {
            "confidence": prediction.confidence,
            "features": prediction.top_features,
            "processing_time_ms": prediction.processing_time_ms,
        }
        await self._event_repo.create(event)

        processing_time = (time.time() - start_time) * 1000

        logger.log_ai_prediction(
            str(incident_id),
            prediction.priority,
            prediction.confidence,
            processing_time,
            prediction.top_features,
        )

        return ClassificationResult(
            incident_id=incident.id,
            priority=prediction.priority,
            priority_label=priority_level.label,
            confidence=prediction.confidence,
            explanation=prediction.reasoning,
            top_features=prediction.top_features,
            processing_time_ms=processing_time,
        )
