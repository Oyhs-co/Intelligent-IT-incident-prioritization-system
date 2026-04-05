"""Caso de uso para buscar incidentes similares."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from uuid import UUID
import time

from src.domain.repositories import IIncidentRepository
from src.shared.logging import get_logger

if TYPE_CHECKING:
    from src.application.ports import IEmbeddingModel
    from src.infrastructure.ml.vector_store import IncidentVectorStore

logger = get_logger("use_cases.search_similar")

SIMILARITY_THRESHOLD = 0.7


@dataclass
class SimilarIncidentResult:
    """Resultado de búsqueda de incidentes similares."""

    incident_id: UUID
    ticket_number: str
    title: str
    description: str
    priority: int
    priority_label: str
    status: str
    similarity_score: float
    category: Optional[str] = None
    resolution_time_hours: Optional[float] = None
    resolution: Optional[str] = None


class SearchSimilarIncidentsUseCase:
    """Busca incidentes similares usando embeddings."""

    def __init__(
        self,
        incident_repository: IIncidentRepository,
        embedding_model: Optional[IEmbeddingModel] = None,
        vector_store: Optional[IncidentVectorStore] = None,
    ):
        self._incident_repo = incident_repository
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    async def execute(
        self,
        query: str,
        incident_id: Optional[UUID] = None,
        limit: int = 5,
        min_similarity: float = SIMILARITY_THRESHOLD,
    ) -> list[SimilarIncidentResult]:
        """Busca incidentes similares."""
        start_time = time.time()

        logger.info("Searching similar incidents", query_length=len(query))

        if self._embedding_model and self._vector_store:
            return await self._search_with_embeddings(
                query, incident_id, limit, min_similarity, start_time
            )

        return await self._search_fallback(query, incident_id, limit, start_time)

    async def _search_with_embeddings(
        self,
        query: str,
        incident_id: Optional[UUID],
        limit: int,
        min_similarity: float,
        start_time: float,
    ) -> list[SimilarIncidentResult]:
        """Busca usando embeddings y vector store."""
        embedding = await self._embedding_model.generate_embedding(query)

        similar = await self._vector_store.search_similar(
            embedding=embedding,
            exclude_id=incident_id,
            limit=limit,
            min_score=min_similarity,
        )

        results = []
        for item in similar:
            incident = await self._incident_repo.get_by_id(item["incident_id"])
            if incident:
                results.append(
                    SimilarIncidentResult(
                        incident_id=incident.id,
                        ticket_number=incident.ticket_number,
                        title=incident.title,
                        description=incident.description[:200] + "..."
                            if len(incident.description) > 200 else incident.description,
                        priority=incident.priority.value if incident.priority else 3,
                        priority_label=incident.priority_label or "Unknown",
                        status=incident.status.value if incident.status else "unknown",
                        similarity_score=item["score"],
                        category=incident.category.value if incident.category else None,
                        resolution_time_hours=item.get("resolution_time_hours"),
                        resolution=item.get("resolution"),
                    )
                )

        processing_time = (time.time() - start_time) * 1000
        logger.log_similarity_search(
            query_length=len(query),
            results_count=len(results),
            processing_time_ms=processing_time,
        )

        return results

    async def _search_fallback(
        self,
        query: str,
        incident_id: Optional[UUID],
        limit: int,
        start_time: float,
    ) -> list[SimilarIncidentResult]:
        """Búsqueda simple por palabras clave."""
        keywords = query.lower().split()
        all_incidents = await self._incident_repo.list(skip=0, limit=1000)

        scored = []
        for incident in all_incidents:
            if incident_id and incident.id == incident_id:
                continue

            text = f"{incident.title} {incident.description}".lower()
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0:
                score = matches / len(keywords)
                if incident.status and incident.status.value in ("resolved", "closed"):
                    scored.append((score, incident))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []

        for score, incident in scored[:limit]:
            results.append(
                SimilarIncidentResult(
                    incident_id=incident.id,
                    ticket_number=incident.ticket_number,
                    title=incident.title,
                    description=incident.description[:200] + "..."
                        if len(incident.description) > 200 else incident.description,
                    priority=incident.priority.value if incident.priority else 3,
                    priority_label=incident.priority_label or "Unknown",
                    status=incident.status.value if incident.status else "unknown",
                    similarity_score=score,
                    category=incident.category.value if incident.category else None,
                )
            )

        processing_time = (time.time() - start_time) * 1000
        logger.log_similarity_search(
            query_length=len(query),
            results_count=len(results),
            processing_time_ms=processing_time,
            fallback=True,
        )

        return results


@dataclass
class SearchSimilarIncidentsRequest:
    """Request para búsqueda de incidentes similares."""

    query: str
    incident_id: Optional[UUID] = None
    limit: int = 5
    min_similarity: float = SIMILARITY_THRESHOLD
