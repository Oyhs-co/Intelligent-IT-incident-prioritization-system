"""Integration tests for repositories."""

from uuid import uuid4

import pytest

from src.domain.entities.incident import Incident
from src.domain.value_objects import IncidentSource, IncidentStatus
from src.infrastructure.database.repositories import IncidentRepository


@pytest.mark.asyncio
async def test_incident_repository_create(
    incident_repository: IncidentRepository,
    session,
):
    """Test creating an incident via repository."""
    incident = Incident()
    incident.title = "Repository Test"
    incident.description = "Testing repository"
    incident.status = IncidentStatus.NEW
    incident.urgency = 2
    incident.impact = 2
    incident.source = IncidentSource.WEB

    created = await incident_repository.create(incident)
    assert created.id is not None
    assert created.ticket_number is not None
    await session.commit()


@pytest.mark.asyncio
async def test_incident_repository_get_by_id(
    incident_repository: IncidentRepository,
    session,
):
    """Test getting an incident by ID."""
    incident = Incident()
    incident.title = "Get By ID Test"
    incident.description = "Testing get by id"
    incident.status = IncidentStatus.NEW
    incident.urgency = 2
    incident.impact = 2
    incident.source = IncidentSource.WEB

    created = await incident_repository.create(incident)
    await session.flush()

    result = await incident_repository.get_by_id(created.id)
    assert result is not None
    assert result.title == "Get By ID Test"

    not_found = await incident_repository.get_by_id(uuid4())
    assert not_found is None


@pytest.mark.asyncio
async def test_incident_repository_update(
    incident_repository: IncidentRepository,
    session,
):
    """Test updating an incident."""
    incident = Incident()
    incident.title = "Original Title"
    incident.description = "Original description"
    incident.status = IncidentStatus.NEW
    incident.urgency = 2
    incident.impact = 2
    incident.source = IncidentSource.WEB

    created = await incident_repository.create(incident)
    await session.flush()

    created.title = "Updated Title"
    updated = await incident_repository.update(created)
    assert updated.title == "Updated Title"


@pytest.mark.asyncio
async def test_incident_repository_delete(
    incident_repository: IncidentRepository,
    session,
):
    """Test deleting an incident."""
    incident = Incident()
    incident.title = "To Delete"
    incident.description = "Will be deleted"
    incident.status = IncidentStatus.NEW
    incident.urgency = 2
    incident.impact = 2
    incident.source = IncidentSource.WEB

    created = await incident_repository.create(incident)
    await session.flush()

    incident_id = created.id
    deleted = await incident_repository.delete(incident_id)
    assert deleted is True

    result = await incident_repository.get_by_id(incident_id)
    assert result is None


@pytest.mark.asyncio
async def test_incident_repository_list(
    incident_repository: IncidentRepository,
    test_incident,
):
    """Test listing incidents."""
    result, total = await incident_repository.list_all(skip=0, limit=10)
    assert total >= 1
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_incident_repository_get_by_ticket_number(
    incident_repository: IncidentRepository,
    test_incident,
):
    """Test getting an incident by ticket number."""
    result = await incident_repository.get_by_ticket_number(test_incident.ticket_number)
    assert result is not None
    assert result.ticket_number == test_incident.ticket_number
