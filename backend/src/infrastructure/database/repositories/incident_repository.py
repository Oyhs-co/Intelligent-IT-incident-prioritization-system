"""Repositorio de incidentes implementado con SQLAlchemy."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.incident import Incident
from src.domain.repositories import IIncidentRepository
from src.domain.value_objects import (
    IncidentCategory,
    IncidentSource,
    IncidentStatus,
    PriorityLevel,
)

from ..models.incident_model import IncidentModel
from ..models.incident_similarity_model import IncidentSimilarityModel


class IncidentRepository(IIncidentRepository):
    """Implementación del repositorio de incidentes."""

    def __init__(self, session: AsyncSession):
        """Inicializa el repositorio con una sesión de base de datos."""
        self._session = session

    @staticmethod
    def _ensure_aware(dt: datetime | None) -> datetime | None:
        if dt is not None and dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt

    def _model_to_entity(self, model: IncidentModel) -> Incident:
        """Convierte modelo ORM a entidad de dominio."""
        incident = Incident()
        incident._id = UUID(model.id)
        incident._ticket_number = model.ticket_number
        incident._title = model.title
        incident._description = model.description
        incident._category = IncidentCategory(model.category) if model.category else None
        incident._subcategory = model.subcategory
        incident._status = IncidentStatus(model.status)
        incident._priority = PriorityLevel(model.priority) if model.priority else None
        incident._suggested_priority = (
            PriorityLevel(model.suggested_priority)
            if model.suggested_priority is not None else None
        )
        incident._ai_model_version = model.ai_model_version
        incident._ai_processed_at = self._ensure_aware(model.ai_processed_at)
        incident._urgency = model.urgency
        incident._impact = model.impact
        incident._confidence_score = model.confidence_score
        incident._explanation = model.explanation
        incident._sla_deadline = self._ensure_aware(model.sla_deadline)
        incident._resolution = model.resolution
        incident._resolution_code = model.resolution_code
        incident._source = IncidentSource(model.source)
        incident._tags = model.tags or []
        incident._metadata = model.custom_metadata or {}
        incident._reporter_id = UUID(model.reporter_id) if model.reporter_id else None
        incident._assigned_to = UUID(model.assigned_to) if model.assigned_to else None
        incident._resolved_by = UUID(model.resolved_by) if model.resolved_by else None
        incident._closed_by = UUID(model.closed_by) if model.closed_by else None
        incident._similar_incidents = [UUID(m.id) for m in model.similar_incidents]
        incident._resolved_at = self._ensure_aware(model.resolved_at)
        incident._closed_at = self._ensure_aware(model.closed_at)
        incident._created_at = self._ensure_aware(model.created_at)
        incident._updated_at = self._ensure_aware(model.updated_at)
        return incident

    def _entity_to_model(self, entity: Incident) -> IncidentModel:
        """Convierte entidad de dominio a modelo ORM."""
        return IncidentModel(
            id=str(entity.id),
            ticket_number=entity.ticket_number,
            title=entity.title,
            description=entity.description,
            category=entity.category.value if entity.category else None,
            subcategory=entity.subcategory,
            status=entity.status.value,
            priority=entity.priority.value if entity.priority else None,
            suggested_priority=(
                entity.suggested_priority.value if entity.suggested_priority else None
            ),
            ai_model_version=entity.ai_model_version,
            ai_processed_at=entity.ai_processed_at,
            urgency=entity.urgency,
            impact=entity.impact,
            confidence_score=entity.confidence_score,
            explanation=entity.explanation,
            sla_deadline=entity.sla_deadline,
            resolution=entity.resolution,
            resolution_code=entity.resolution_code,
            source=entity.source.value,
            tags=entity.tags,
            custom_metadata=entity.metadata,
            reporter_id=str(entity.reporter_id) if entity.reporter_id else None,
            assigned_to=str(entity.assigned_to) if entity.assigned_to else None,
            resolved_by=str(entity.resolved_by) if entity.resolved_by else None,
            closed_by=str(entity.closed_by) if entity.closed_by else None,
            # fix: similar_incidents eliminado — se gestiona via IncidentSimilarityModel
            resolved_at=entity.resolved_at,
            closed_at=entity.closed_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, incident: Incident) -> Incident:
        """Crea un nuevo incidente."""
        model = self._entity_to_model(incident)
        next_seq = (await self._session.execute(
            select(func.max(IncidentModel.ticket_seq))
        )).scalar_one_or_none() or 0
        model.ticket_seq = next_seq + 1
        model.ticket_number = f"INC-{next_seq + 1:05d}"
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, incident_id: UUID) -> Incident | None:
        """Obtiene un incidente por su ID."""
        stmt = select(IncidentModel).options(
            selectinload(IncidentModel.similar_incidents),
        ).where(IncidentModel.id == str(incident_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_ticket_number(self, ticket_number: str) -> Incident | None:
        """Obtiene un incidente por su número de ticket."""
        stmt = select(IncidentModel).options(
            selectinload(IncidentModel.similar_incidents),
        ).where(IncidentModel.ticket_number == ticket_number)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def update(self, incident: Incident) -> Incident:
        """Actualiza un incidente existente."""
        stmt = select(IncidentModel).options(
            selectinload(IncidentModel.similar_incidents),
        ).where(IncidentModel.id == str(incident.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Incident {incident.id} not found")

        model.ticket_number = incident.ticket_number
        model.title = incident.title
        model.description = incident.description
        model.category = incident.category.value if incident.category else None
        model.subcategory = incident.subcategory
        model.status = incident.status.value
        model.priority = incident.priority.value if incident.priority else None
        model.suggested_priority = (
            incident.suggested_priority.value if incident.suggested_priority else None
        )
        model.ai_model_version = incident.ai_model_version
        model.ai_processed_at = incident.ai_processed_at
        model.urgency = incident.urgency
        model.impact = incident.impact
        model.confidence_score = incident.confidence_score
        model.explanation = incident.explanation
        model.sla_deadline = incident.sla_deadline
        model.resolution = incident.resolution
        model.resolution_code = incident.resolution_code
        model.tags = incident.tags
        model.source = incident.source.value
        model.custom_metadata = incident.metadata
        model.assigned_to = str(incident.assigned_to) if incident.assigned_to else None
        model.resolved_by = str(incident.resolved_by) if incident.resolved_by else None
        model.closed_by = str(incident.closed_by) if incident.closed_by else None
        model.resolved_at = incident.resolved_at
        model.closed_at = incident.closed_at

        # Sincronizar incidentes similares (relación muchos a muchos)
        stmt_sim = select(IncidentSimilarityModel.similar_id).where(
            IncidentSimilarityModel.incident_id == str(incident.id),
        )
        result_sim = await self._session.execute(stmt_sim)
        existing_sim_ids = {row[0] for row in result_sim}
        new_sim_ids = {str(s) for s in incident.similar_incidents}
        for sim_id in new_sim_ids - existing_sim_ids:
            self._session.add(IncidentSimilarityModel(
                incident_id=str(incident.id), similar_id=sim_id,
            ))
        for sim_id in existing_sim_ids - new_sim_ids:
            stmt_del = select(IncidentSimilarityModel).where(
                IncidentSimilarityModel.incident_id == str(incident.id),
                IncidentSimilarityModel.similar_id == sim_id,
            )
            result_del = await self._session.execute(stmt_del)
            sim_model = result_del.scalar_one_or_none()
            if sim_model:
                await self._session.delete(sim_model)

        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, incident_id: UUID) -> bool:
        """Elimina un incidente."""
        stmt = select(IncidentModel).where(IncidentModel.id == str(incident_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True

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
        """Lista incidentes con filtros."""
        stmt = select(IncidentModel).options(
            selectinload(IncidentModel.similar_incidents),
        )
        count_stmt = select(func.count(IncidentModel.id))

        if status:
            stmt = stmt.where(IncidentModel.status == status)
            count_stmt = count_stmt.where(IncidentModel.status == status)
        if priority is not None:
            stmt = stmt.where(IncidentModel.priority == priority)
            count_stmt = count_stmt.where(IncidentModel.priority == priority)
        if category:
            stmt = stmt.where(IncidentModel.category == category)
            count_stmt = count_stmt.where(IncidentModel.category == category)
        if assigned_to:
            stmt = stmt.where(IncidentModel.assigned_to == str(assigned_to))
            count_stmt = count_stmt.where(IncidentModel.assigned_to == str(assigned_to))
        if created_by:
            stmt = stmt.where(IncidentModel.reporter_id == str(created_by))
            count_stmt = count_stmt.where(IncidentModel.reporter_id == str(created_by))

        stmt = stmt.order_by(IncidentModel.created_at.desc()).offset(skip).limit(limit)

        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models], total

    async def get_next_ticket_number(self) -> str:
        """Genera el siguiente número de ticket usando secuencia atómica."""
        stmt = select(func.max(IncidentModel.ticket_seq))
        result = await self._session.execute(stmt)
        last_seq = result.scalar_one_or_none() or 0
        return f"INC-{last_seq + 1:05d}"

    async def count_by_status(self) -> dict[str, int]:
        """Cuenta incidentes agrupados por estado."""
        stmt = select(
            IncidentModel.status, func.count(IncidentModel.id)
        ).group_by(IncidentModel.status)
        result = await self._session.execute(stmt)
        return {row[0]: row[1] for row in result}

    async def count_by_priority(self) -> dict[int, int]:
        """Cuenta incidentes agrupados por prioridad."""
        stmt = select(
            IncidentModel.priority, func.count(IncidentModel.id)
        ).where(
            IncidentModel.priority.isnot(None)
        ).group_by(IncidentModel.priority)
        result = await self._session.execute(stmt)
        return {row[0]: row[1] for row in result}

    async def count_by_category(self) -> dict[str, int]:
        """Cuenta incidentes agrupados por categoría."""
        stmt = select(
            IncidentModel.category, func.count(IncidentModel.id)
        ).where(
            IncidentModel.category.isnot(None)
        ).group_by(IncidentModel.category)
        result = await self._session.execute(stmt)
        return {row[0]: row[1] for row in result}

    async def sla_breach_count(self) -> int:
        """Cuenta incidentes con SLA incumplido (deadline pasado y no resueltos)."""
        stmt = select(func.count(IncidentModel.id)).where(
            IncidentModel.sla_deadline.isnot(None),
            IncidentModel.sla_deadline < datetime.now(UTC),
            IncidentModel.status.notin_(["resolved", "closed", "rejected"]),
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
