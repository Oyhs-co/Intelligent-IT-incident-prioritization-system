"""Caso de uso para obtener recomendaciones basadas en incidentes similares."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional
from uuid import UUID
import time

from src.shared.logging import get_logger

if TYPE_CHECKING:
    from src.domain.repositories import IIncidentRepository
    from src.application.ports import IEmbeddingModel, ILLMClient
    from src.infrastructure.ml.vector_store import IncidentVectorStore

logger = get_logger("use_cases.recommendations")


@dataclass
class RecommendationResult:
    """Resultado de recomendaciones."""

    incident_id: UUID
    recommended_priority: int
    recommended_priority_label: str
    confidence: float
    similar_incidents_count: int
    avg_resolution_time_hours: float
    suggested_actions: list[str]
    explanation: str
    processing_time_ms: float


@dataclass
class GetRecommendationsRequest:
    """Request para obtener recomendaciones."""

    incident_id: UUID
    include_llm_explanation: bool = True


class GetRecommendationsUseCase:
    """Obtiene recomendaciones basadas en incidentes similares."""

    def __init__(
        self,
        incident_repository: IIncidentRepository,
        embedding_model: Optional[IEmbeddingModel] = None,
        vector_store: Optional[IncidentVectorStore] = None,
        llm_client: Optional[ILLMClient] = None,
    ):
        self._incident_repo = incident_repository
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._llm_client = llm_client

    async def execute(
        self,
        request: GetRecommendationsRequest,
    ) -> RecommendationResult:
        """Ejecuta la generación de recomendaciones."""
        start_time = time.time()

        logger.info("Generating recommendations", incident_id=str(request.incident_id))

        incident = await self._incident_repo.get_by_id(request.incident_id)
        if incident is None:
            raise ValueError(f"Incident {request.incident_id} not found")

        similar = await self._find_similar_incidents(incident)
        priority, confidence = self._calculate_priority(similar)
        actions = self._generate_suggested_actions(similar, incident)
        resolution_time = self._calculate_avg_resolution_time(similar)

        explanation = ""
        if request.include_llm_explanation and self._llm_client:
            explanation = await self._generate_explanation(incident, similar, priority, confidence)
        else:
            explanation = self._default_explanation(priority, len(similar))

        processing_time = (time.time() - start_time) * 1000

        logger.info(
            "Recommendations generated",
            incident_id=str(request.incident_id),
            similar_count=len(similar),
            recommended_priority=priority,
            processing_time_ms=processing_time,
        )

        from src.domain.value_objects import PriorityLevel

        return RecommendationResult(
            incident_id=incident.id,
            recommended_priority=priority,
            recommended_priority_label=PriorityLevel.from_int(priority).label,
            confidence=confidence,
            similar_incidents_count=len(similar),
            avg_resolution_time_hours=resolution_time,
            suggested_actions=actions,
            explanation=explanation,
            processing_time_ms=processing_time,
        )

    async def _find_similar_incidents(self, incident) -> list:
        """Busca incidentes similares."""
        if self._embedding_model and self._vector_store:
            text = f"{incident.title} {incident.description}"
            embedding = await self._embedding_model.generate_embedding(text)
            similar = await self._vector_store.search_similar(
                embedding=embedding,
                exclude_id=incident.id,
                limit=10,
                min_score=0.5,
            )
            results = []
            for item in similar:
                inc = await self._incident_repo.get_by_id(item["incident_id"])
                if inc:
                    results.append(inc)
            return results

        all_incidents = await self._incident_repo.list(skip=0, limit=100)
        keywords = f"{incident.title} {incident.description}".lower().split()
        scored = []

        for inc in all_incidents:
            if inc.id == incident.id:
                continue
            text = f"{inc.title} {inc.description}".lower()
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0:
                scored.append((matches / len(keywords), inc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [inc for _, inc in scored[:10]]

    def _calculate_priority(self, similar_incidents: list) -> tuple[int, float]:
        """Calcula prioridad recomendada basándose en similares."""
        if not similar_incidents:
            return 3, 0.5

        priorities = []
        for inc in similar_incidents:
            if inc.priority:
                priorities.append(inc.priority.value)

        if not priorities:
            return 3, 0.5

        avg_priority = sum(priorities) / len(priorities)
        recommended = max(1, min(4, round(avg_priority)))
        confidence = min(0.95, 0.5 + (len(similar_incidents) * 0.05))

        return recommended, confidence

    def _calculate_avg_resolution_time(self, similar_incidents: list) -> float:
        """Calcula tiempo promedio de resolución."""
        resolved = [
            inc for inc in similar_incidents
            if inc.resolved_at and inc.created_at
        ]
        if not resolved:
            return 0.0

        total_hours = sum(
            (inc.resolved_at - inc.created_at).total_seconds() / 3600
            for inc in resolved
        )
        return total_hours / len(resolved)

    def _generate_suggested_actions(self, similar: list, incident) -> list[str]:
        """Genera acciones sugeridas basadas en similares."""
        actions = []

        resolved_similar = [inc for inc in similar if inc.status and inc.status.value in ("resolved", "closed")]

        if len(resolved_similar) >= 3:
            actions.append("Consider following the resolution pattern from similar resolved incidents")
        else:
            actions.append("Review similar open incidents for potential workaround")

        categories = {inc.category for inc in similar if inc.category}
        if incident.category in categories:
            actions.append("Category matches resolved incidents - standard procedure may apply")

        if incident.urgency >= 4 or incident.impact >= 4:
            actions.append("High urgency/impact detected - escalate if no response within 1 hour")

        if not resolved_similar:
            actions.append("No resolved similar incidents - consider creating a new knowledge article")

        return actions[:5]

    async def _generate_explanation(
        self,
        incident,
        similar: list,
        priority: int,
        confidence: float,
    ) -> str:
        """Genera explicación usando LLM."""
        try:
            similar_data = [
                {
                    "title": inc.title,
                    "priority": inc.priority.value if inc.priority else 3,
                    "status": inc.status.value if inc.status else "unknown",
                }
                for inc in similar[:5]
            ]

            return await self._llm_client.generate_explanation(
                incident_data={
                    "title": incident.title,
                    "description": incident.description,
                    "urgency": incident.urgency,
                    "impact": incident.impact,
                },
                similar_incidents=similar_data,
                priority=priority,
                confidence=confidence,
            )
        except Exception as e:
            logger.warning(f"LLM explanation failed: {e}")
            return self._default_explanation(priority, len(similar))

    def _default_explanation(self, priority: int, similar_count: int) -> str:
        """Genera explicación por defecto."""
        return (
            f"Based on {similar_count} similar incident(s), "
            f"priority {priority} is recommended. "
            f"This recommendation has a confidence of {similar_count * 5 + 50:.0f}%"
            f" due to the number of similar cases found."
        )
