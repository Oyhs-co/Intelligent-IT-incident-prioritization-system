"""Tests de integración para IncidentRepository."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from uuid import uuid4

import pytest

from src.domain.entities.incident import Incident
from src.domain.value_objects import (
    IncidentCategory,
    IncidentSource,
    IncidentStatus,
    PriorityLevel,
)
from src.infrastructure.database.repositories.incident_repository import (
    IncidentRepository,
)


def _make_incident(**kwargs) -> Incident:
    """Crea un Incident con valores mínimos para pruebas."""
    i = Incident()
    defaults = {
        "title": "Incidente de prueba",
        "description": "Descripción del incidente de prueba",
    }
    for k, v in {**defaults, **kwargs}.items():
        setattr(i, k, v)
    return i


class TestIncidentRepositoryCreate:
    """Tests de creación de incidentes."""

    async def test_create_incident(self, session):
        """Crear un incidente debe persistirlo y asignarle un ID."""
        repo = IncidentRepository(session)
        incident = _make_incident()
        created = await repo.create(incident)
        assert created.id is not None
        assert created.title == "Incidente de prueba"

    async def test_create_with_all_fields(self, session):
        """Crear con todos los campos debe persistirlos correctamente."""
        repo = IncidentRepository(session)
        incident = _make_incident(
            title="Incidente completo",
            description="Descripción completa",
        )
        incident.assign_priority(
            priority=PriorityLevel.P4_CRITICAL,
            confidence=0.95,
            explanation="Alta prioridad",
        )
        incident.category = IncidentCategory.SECURITY
        incident.source = IncidentSource.API
        incident.add_tag("urgente")
        created = await repo.create(incident)
        assert created.priority == PriorityLevel.P4_CRITICAL
        assert created.confidence_score == 0.95
        assert created.category == IncidentCategory.SECURITY
        assert created.source == IncidentSource.API
        assert "urgente" in created.tags


class TestIncidentRepositoryGetById:
    """Tests de búsqueda por ID."""

    async def test_get_by_id_found(self, session):
        """Obtener por ID existente debe retornar el incidente."""
        repo = IncidentRepository(session)
        incident = _make_incident()
        created = await repo.create(incident)
        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.title == created.title

    async def test_get_by_id_not_found(self, session):
        """Obtener por ID inexistente debe retornar None."""
        repo = IncidentRepository(session)
        result = await repo.get_by_id(uuid4())
        assert result is None

    async def test_get_by_ticket_number(self, session):
        """Obtener por ticket number debe retornar el incidente."""
        repo = IncidentRepository(session)
        incident = _make_incident()
        created = await repo.create(incident)
        found = await repo.get_by_ticket_number(created.ticket_number)
        assert found is not None
        assert found.ticket_number == created.ticket_number


class TestIncidentRepositoryUpdate:
    """Tests de actualización de incidentes."""

    async def test_update_all_fields(self, session):
        """Actualizar todos los campos debe persistirlos."""
        repo = IncidentRepository(session)
        incident = _make_incident()
        created = await repo.create(incident)
        created.title = "Título actualizado"
        created.description = "Descripción actualizada"
        created.category = IncidentCategory.NETWORK
        created.source = IncidentSource.EMAIL
        created.add_tag("critico")
        created.metadata = {"ambiente": "produccion"}
        await repo.update(created)
        updated = await repo.get_by_id(created.id)
        assert updated is not None
        assert updated.title == "Título actualizado"
        assert updated.category == IncidentCategory.NETWORK
        assert updated.source == IncidentSource.EMAIL
        assert "critico" in updated.tags
        assert updated.metadata == {"ambiente": "produccion"}

    async def test_update_not_found(self, session):
        """Actualizar incidente inexistente debe lanzar ValueError."""
        repo = IncidentRepository(session)
        incident = _make_incident()
        object.__setattr__(incident, "_id", uuid4())
        with pytest.raises(ValueError, match="not found"):
            await repo.update(incident)


class TestIncidentRepositoryDelete:
    """Tests de eliminación de incidentes."""

    async def test_delete_exists(self, session):
        """Eliminar un incidente existente debe retornar True."""
        repo = IncidentRepository(session)
        incident = _make_incident()
        created = await repo.create(incident)
        result = await repo.delete(created.id)
        assert result is True
        found = await repo.get_by_id(created.id)
        assert found is None

    async def test_delete_not_found(self, session):
        """Eliminar un incidente inexistente debe retornar False."""
        repo = IncidentRepository(session)
        result = await repo.delete(uuid4())
        assert result is False


class TestIncidentRepositoryListAll:
    """Tests de listado con filtros."""

    async def test_list_all_no_filters(self, session):
        """Listar sin filtros debe retornar todos."""
        repo = IncidentRepository(session)
        i1 = _make_incident(title="Incidente 1")
        i2 = _make_incident(title="Incidente 2")
        await repo.create(i1)
        await repo.create(i2)
        items, total = await repo.list_all()
        assert total >= 2
        assert len(items) >= 2

    async def test_list_all_with_status_filter(self, session):
        """Filtrar por estado debe retornar solo los que coinciden."""
        repo = IncidentRepository(session)
        i1 = _make_incident(title="Abierto")
        i2 = _make_incident(title="Resuelto")
        await repo.create(i1)
        await repo.create(i2)
        i2.resolve("resuelto", uuid4())
        await repo.update(i2)
        items, total = await repo.list_all(status="resolved")
        assert all(item.status == IncidentStatus.RESOLVED for item in items)

    async def test_list_all_pagination(self, session):
        """La paginación debe funcionar correctamente."""
        repo = IncidentRepository(session)
        for i in range(5):
            await repo.create(_make_incident(title=f"Incidente {i}"))
        items, total = await repo.list_all(skip=0, limit=2)
        assert len(items) == 2
        assert total >= 5


class TestIncidentRepositoryTicketNumber:
    """Tests de generación de ticket number."""

    async def test_get_next_ticket_number(self, session):
        """El ticket number debe ser secuencial."""
        repo = IncidentRepository(session)
        t1 = await repo.get_next_ticket_number()
        assert t1.startswith("INC-")
        seq1 = int(t1.split("-")[1])
        i = _make_incident()
        await repo.create(i)
        t2 = await repo.get_next_ticket_number()
        seq2 = int(t2.split("-")[1])
        assert seq2 > seq1


class TestIncidentRepositoryCounts:
    """Tests de queries agregadas."""

    async def test_count_by_status(self, session):
        """count_by_status debe agrupar correctamente."""
        repo = IncidentRepository(session)
        await repo.create(_make_incident(title="A"))
        await repo.create(_make_incident(title="B"))
        counts = await repo.count_by_status()
        assert "new" in counts
        assert counts["new"] >= 2

    async def test_count_by_priority(self, session):
        """count_by_priority debe agrupar correctamente."""
        repo = IncidentRepository(session)
        i = _make_incident(title="Prioritario")
        i.assign_priority(PriorityLevel.P4_CRITICAL, 0.9, "test")
        await repo.create(i)
        counts = await repo.count_by_priority()
        assert 4 in counts
        assert counts[4] >= 1

    async def test_count_by_category(self, session):
        """count_by_category debe agrupar correctamente."""
        repo = IncidentRepository(session)
        i = _make_incident(title="Categorizado")
        i.category = IncidentCategory.SECURITY
        await repo.create(i)
        counts = await repo.count_by_category()
        assert "security" in counts
        assert counts["security"] >= 1

    async def test_sla_breach_count(self, session):
        """sla_breach_count debe contar incidentes con SLA vencido."""
        repo = IncidentRepository(session)
        i = _make_incident(title="Vencido")
        i.assign_priority(PriorityLevel.P4_CRITICAL, 0.9, "test")
        object.__setattr__(i, "_sla_deadline", datetime.now(timezone.utc) - timedelta(hours=1))
        await repo.create(i)
        count = await repo.sla_breach_count()
        assert count >= 1
