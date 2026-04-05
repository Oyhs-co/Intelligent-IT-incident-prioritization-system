"""Integration tests for incident endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_incident(client: AsyncClient):
    """Test creating an incident via API."""
    payload = {
        "title": "Integration Test Incident",
        "description": "This is a test incident for integration testing",
        "urgency": 4,
        "impact": 3,
        "source": "api",
    }

    response = await client.post("/api/v1/incidents/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == "new"
    assert "id" in data
    assert "ticket_number" in data


@pytest.mark.asyncio
async def test_list_incidents(client: AsyncClient):
    """Test listing incidents."""
    response = await client.get("/api/v1/incidents/")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


@pytest.mark.asyncio
async def test_list_incidents_with_filters(client: AsyncClient):
    """Test listing incidents with filters."""
    response = await client.get(
        "/api/v1/incidents/",
        params={"status": "open", "priority": 2, "limit": 10},
    )
    assert response.status_code == 200

    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_get_incident_not_found(client: AsyncClient):
    """Test getting a non-existent incident."""
    from uuid import uuid4

    response = await client.get(f"/api/v1/incidents/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_incident_validation(client: AsyncClient):
    """Test incident creation with invalid data."""
    payload = {
        "title": "",
        "description": "Test",
    }

    response = await client.post("/api/v1/incidents/", json=payload)
    assert response.status_code == 422
