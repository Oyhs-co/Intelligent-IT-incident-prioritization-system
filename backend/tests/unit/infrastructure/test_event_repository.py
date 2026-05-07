"""Tests de integración para EventRepository."""

from __future__ import annotations

from uuid import uuid4

import pytest

from src.domain.entities.incident import Incident
from src.domain.entities.incident_event import IncidentEvent
from src.domain.value_objects import EventType
from src.infrastructure.database.repositories.event_repository import EventRepository
from src.infrastructure.database.repositories.incident_repository import (
    IncidentRepository,
)


class TestEventRepository:
    """Tests del repositorio de eventos."""

    async def _create_incident(self, session) -> Incident:
        """Crea un incidente de prueba y lo retorna."""
        repo = IncidentRepository(session)
        i = Incident()
        i.title = "Incidente para eventos"
        i.description = "Descripción"
        return await repo.create(i)

    async def test_create_event(self, session):
        """Crear un evento debe persistirlo."""
        repo = EventRepository(session)
        incident = await self._create_incident(session)
        event = IncidentEvent(
            _incident_id=incident.id,
            _event_type=EventType.CREATED,
        )
        created = await repo.create(event)
        assert created.id is not None
        assert created.event_type == EventType.CREATED

    async def test_create_event_with_values(self, session):
        """Crear evento con old/new values debe persistirlos."""
        repo = EventRepository(session)
        incident = await self._create_incident(session)
        event = IncidentEvent(
            _incident_id=incident.id,
            _event_type=EventType.PRIORITY_CHANGED,
            _old_value="3",
            _new_value="4",
            _user_id=uuid4(),
        )
        created = await repo.create(event)
        assert created.old_value == "3"
        assert created.new_value == "4"
        assert created.user_id is not None

    async def test_list_by_incident(self, session):
        """Listar eventos de un incidente debe retornarlos ordenados."""
        repo = EventRepository(session)
        incident = await self._create_incident(session)
        e1 = IncidentEvent(_incident_id=incident.id, _event_type=EventType.CREATED)
        e2 = IncidentEvent(
            _incident_id=incident.id, _event_type=EventType.PRIORITY_CHANGED,
        )
        await repo.create(e1)
        await repo.create(e2)
        items, total = await repo.list_by_incident(incident.id)
        assert total == 2
        assert len(items) == 2

    async def test_list_by_incident_other_incident_not_included(self, session):
        """Eventos de otro incidente no deben aparecer."""
        repo = EventRepository(session)
        inc1 = await self._create_incident(session)
        inc2 = await self._create_incident(session)
        e1 = IncidentEvent(_incident_id=inc1.id, _event_type=EventType.CREATED)
        await repo.create(e1)
        items, total = await repo.list_by_incident(inc2.id)
        assert total == 0

    async def test_list_by_incident_pagination(self, session):
        """La paginación debe funcionar."""
        repo = EventRepository(session)
        incident = await self._create_incident(session)
        for i in range(5):
            await repo.create(IncidentEvent(
                _incident_id=incident.id,
                _event_type=EventType.CREATED,
            ))
        items, total = await repo.list_by_incident(incident.id, skip=0, limit=2)
        assert len(items) == 2
        assert total == 5
