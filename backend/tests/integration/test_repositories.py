"""Integration tests for repositories."""

import pytest
from uuid import uuid4
from datetime import datetime

from src.infrastructure.database.repositories import IncidentRepository
from src.infrastructure.database.models import IncidentModel


@pytest.mark.asyncio
async def test_incident_repository_create(
    incident_repository: IncidentRepository,
    session,
):
    """Test creating an incident via repository."""
    incident = IncidentModel(
        id=uuid4(),
        ticket_number="TEST-001",
        title="Repository Test",
        description="Testing repository",
        status="new",
        urgency=2,
        impact=2,
        source="test",
    )

    created = await incident_repository.create(incident)
    assert created.id == incident.id
    assert created.ticket_number == "TEST-001"
    await session.commit()


@pytest.mark.asyncio
async def test_incident_repository_get_by_id(
    incident_repository: IncidentRepository,
    test_incident: IncidentModel,
):
    """Test getting an incident by ID."""
    result = await incident_repository.get_by_id(test_incident.id)
    assert result is not None
    assert result.id == test_incident.id
    assert result.title == test_incident.title


@pytest.mark.asyncio
async def test_incident_repository_update(
    incident_repository: IncidentRepository,
    test_incident: IncidentModel,
    session,
):
    """Test updating an incident."""
    test_incident.status = "in_progress"
    test_incident.priority = 2

    updated = await incident_repository.update(test_incident)
    assert updated.status == "in_progress"
    assert updated.priority == 2


@pytest.mark.asyncio
async def test_incident_repository_delete(
    incident_repository: IncidentRepository,
    test_incident: IncidentModel,
    session,
):
    """Test deleting an incident."""
    incident_id = test_incident.id

    await incident_repository.delete(incident_id)
    await session.commit()

    result = await incident_repository.get_by_id(incident_id)
    assert result is None


@pytest.mark.asyncio
async def test_incident_repository_list(
    incident_repository: IncidentRepository,
    test_incident: IncidentModel,
):
    """Test listing incidents."""
    result = await incident_repository.list(skip=0, limit=10)
    assert result.total >= 1
    assert len(result.items) >= 1


@pytest.mark.asyncio
async def test_incident_repository_get_by_ticket_number(
    incident_repository: IncidentRepository,
    test_incident: IncidentModel,
):
    """Test getting an incident by ticket number."""
    result = await incident_repository.get_by_ticket_number(test_incident.ticket_number)
    assert result is not None
    assert result.ticket_number == test_incident.ticket_number
