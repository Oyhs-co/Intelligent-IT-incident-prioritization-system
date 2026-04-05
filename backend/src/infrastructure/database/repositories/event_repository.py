"""Repositorio de eventos de incidentes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.incident_event import IncidentEvent
from src.domain.repositories import IIncidentEventRepository
from src.domain.value_objects import EventType
from ..models.incident_event_model import IncidentEventModel

if TYPE_CHECKING:
    pass


class EventRepository(IIncidentEventRepository):
    """Implementación del repositorio de eventos."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _model_to_entity(self, model: IncidentEventModel) -> IncidentEvent:
        """Convierte modelo ORM a entidad de dominio."""
        event = IncidentEvent()
        event._id = UUID(model.id)
        event._incident_id = UUID(model.incident_id)
        event._event_type = EventType(model.event_type)
        event._old_value = model.old_value
        event._new_value = model.new_value
        event._user_id = UUID(model.user_id) if model.user_id else None
        event._metadata = model.metadata or {}
        event._created_at = model.created_at
        return event

    def _entity_to_model(self, entity: IncidentEvent) -> IncidentEventModel:
        """Convierte entidad de dominio a modelo ORM."""
        return IncidentEventModel(
            id=str(entity.id),
            incident_id=str(entity.incident_id),
            event_type=entity.event_type.value,
            old_value=entity.old_value,
            new_value=entity.new_value,
            user_id=str(entity.user_id) if entity.user_id else None,
            metadata=entity.metadata,
            created_at=entity.created_at,
        )

    async def create(self, event: IncidentEvent) -> IncidentEvent:
        """Crea un nuevo evento."""
        model = self._entity_to_model(event)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def list_by_incident(
        self,
        incident_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[IncidentEvent], int]:
        """Lista eventos de un incidente."""
        stmt = select(IncidentEventModel).where(
            IncidentEventModel.incident_id == str(incident_id)
        )
        count_stmt = select(func.count(IncidentEventModel.id)).where(
            IncidentEventModel.incident_id == str(incident_id)
        )

        stmt = stmt.order_by(IncidentEventModel.created_at.desc()).offset(skip).limit(limit)

        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        events = [self._model_to_entity(m) for m in models]
        return events, total
