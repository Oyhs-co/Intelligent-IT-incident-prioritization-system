"""Repositorio de incidentes implementado con SQLAlchemy."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.incident import Incident
from src.domain.entities.user import User
from src.domain.repositories import IIncidentRepository
from src.domain.value_objects import (
    IncidentCategory,
    IncidentSource,
    IncidentStatus,
    PriorityLevel,
)
from ..models.incident_model import IncidentModel

if TYPE_CHECKING:
    pass


class IncidentRepository(IIncidentRepository):
    """Implementación del repositorio de incidentes."""

    def __init__(self, session: AsyncSession):
        self._session = session

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
        incident._urgency = model.urgency
        incident._impact = model.impact
        incident._confidence_score = model.confidence_score
        incident._explanation = model.explanation
        incident._sla_deadline = model.sla_deadline
        incident._resolution = model.resolution
        incident._resolution_code = model.resolution_code
        incident._source = IncidentSource(model.source)
        incident._tags = model.tags or []
        incident._metadata = model.custom_metadata or {}
        incident._reporter_id = UUID(model.reporter_id) if model.reporter_id else None
        incident._assigned_to = UUID(model.assigned_to) if model.assigned_to else None
        incident._resolved_by = UUID(model.resolved_by) if model.resolved_by else None
        incident._closed_by = UUID(model.closed_by) if model.closed_by else None
        incident._similar_incidents = [UUID(x) for x in (model.similar_incidents or [])]
        incident._resolved_at = model.resolved_at
        incident._closed_at = model.closed_at
        incident._created_at = model.created_at
        incident._updated_at = model.updated_at
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
            similar_incidents=[str(x) for x in entity.similar_incidents],
            resolved_at=entity.resolved_at,
            closed_at=entity.closed_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, incident: Incident) -> Incident:
        """Crea un nuevo incidente."""
        model = self._entity_to_model(incident)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, incident_id: UUID) -> Optional[Incident]:
        """Obtiene un incidente por su ID."""
        stmt = select(IncidentModel).where(IncidentModel.id == str(incident_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._model_to_entity(model)

    async def get_by_ticket_number(self, ticket_number: str) -> Optional[Incident]:
        """Obtiene un incidente por su número de ticket."""
        stmt = select(IncidentModel).where(IncidentModel.ticket_number == ticket_number)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._model_to_entity(model)

    async def update(self, incident: Incident) -> Incident:
        """Actualiza un incidente existente."""
        stmt = select(IncidentModel).where(IncidentModel.id == str(incident.id))
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
        model.urgency = incident.urgency
        model.impact = incident.impact
        model.confidence_score = incident.confidence_score
        model.explanation = incident.explanation
        model.sla_deadline = incident.sla_deadline
        model.resolution = incident.resolution
        model.resolution_code = incident.resolution_code
        model.assigned_to = str(incident.assigned_to) if incident.assigned_to else None
        model.resolved_by = str(incident.resolved_by) if incident.resolved_by else None
        model.closed_by = str(incident.closed_by) if incident.closed_by else None
        model.similar_incidents = [str(x) for x in incident.similar_incidents]
        model.resolved_at = incident.resolved_at
        model.closed_at = incident.closed_at

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
        status: Optional[str] = None,
        priority: Optional[int] = None,
        category: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
    ) -> tuple[list[Incident], int]:
        """Lista incidentes con filtros."""
        stmt = select(IncidentModel)
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

        incidents = [self._model_to_entity(m) for m in models]
        return incidents, total

    async def get_next_ticket_number(self) -> str:
        """Genera el siguiente número de ticket."""
        stmt = select(func.max(IncidentModel.ticket_number))
        result = await self._session.execute(stmt)
        last_ticket = result.scalar_one_or_none()

        if last_ticket is None:
            return "INC-00001"

        try:
            last_num = int(last_ticket.split("-")[1])
            next_num = last_num + 1
            return f"INC-{next_num:05d}"
        except (ValueError, IndexError):
            return "INC-00001"
