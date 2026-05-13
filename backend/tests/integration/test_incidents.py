"""Tests de integración para rutas de incidentes."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture
async def _auth_token(client: AsyncClient) -> str:
    """Crea un usuario y retorna su token de acceso."""
    email = f"incident_user_{uuid4().hex[:8]}@test.com"
    await client.post("/api/v1/auth/register", json={
        "email": email, "username": f"incuser_{uuid4().hex[:8]}",
        "password": "SecurePass123!",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": email, "password": "SecurePass123!",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_create_incident(client: AsyncClient):
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
async def test_create_incident_with_auth(client: AsyncClient, _auth_token: str):
    payload = {
        "title": "Auth Incident",
        "description": "Created with auth",
        "urgency": 2,
        "impact": 4,
    }
    response = await client.post(
        "/api/v1/incidents/", json=payload,
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Auth Incident"


@pytest.mark.asyncio
async def test_list_incidents(client: AsyncClient):
    response = await client.get("/api/v1/incidents/")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


@pytest.mark.asyncio
async def test_list_incidents_with_filters(client: AsyncClient):
    response = await client.get(
        "/api/v1/incidents/",
        params={"status": "open", "priority": 2, "limit": 10},
    )
    assert response.status_code == 200
    assert "items" in response.json()


@pytest.mark.asyncio
async def test_get_incident_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/incidents/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_incident_validation(client: AsyncClient):
    payload = {"title": "", "description": "Test"}
    response = await client.post("/api/v1/incidents/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_incident(client: AsyncClient, _auth_token: str):
    create_resp = await client.post("/api/v1/incidents/", json={
        "title": "Original Title",
        "description": "Original desc",
        "urgency": 3,
        "impact": 3,
    })
    inc_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/incidents/{inc_id}",
        json={"title": "Updated Title", "description": "Updated desc"},
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated desc"


@pytest.mark.asyncio
async def test_update_incident_not_found(client: AsyncClient, _auth_token: str):
    response = await client.put(
        f"/api/v1/incidents/{uuid4()}",
        json={"title": "Nope"},
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_incident(client: AsyncClient, _auth_token: str):
    create_resp = await client.post("/api/v1/incidents/", json={
        "title": "To Delete", "description": "Delete me", "urgency": 2, "impact": 2,
    })
    inc_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/incidents/{inc_id}",
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_incident_not_found(client: AsyncClient, _auth_token: str):
    response = await client.delete(
        f"/api/v1/incidents/{uuid4()}",
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_classify_incident(client: AsyncClient, _auth_token: str):
    create_resp = await client.post("/api/v1/incidents/", json={
        "title": "Classify Me", "description": "Classify this incident",
        "urgency": 4, "impact": 4,
    })
    inc_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/v1/incidents/{inc_id}/classify",
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == inc_id
    assert "priority" in data


@pytest.mark.asyncio
async def test_get_recommendations(client: AsyncClient, _auth_token: str):
    create_resp = await client.post("/api/v1/incidents/", json={
        "title": "Recommend Me", "description": "Get recommendations",
        "urgency": 3, "impact": 3,
    })
    inc_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/v1/incidents/{inc_id}/recommendations",
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "incident_id" in data
    assert "recommended_priority" in data


@pytest.mark.asyncio
async def test_get_recommendations_not_found(client: AsyncClient, _auth_token: str):
    response = await client.post(
        f"/api/v1/incidents/{uuid4()}/recommendations",
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_similar(client: AsyncClient, _auth_token: str):
    response = await client.post(
        "/api/v1/incidents/similar",
        json={"query": "Test incident description", "limit": 5},
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_incident_events(client: AsyncClient, _auth_token: str):
    create_resp = await client.post("/api/v1/incidents/", json={
        "title": "Events Test", "description": "Test events",
        "urgency": 2, "impact": 2,
    })
    inc_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/v1/incidents/{inc_id}/events",
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_comments(client: AsyncClient, _auth_token: str):
    create_resp = await client.post("/api/v1/incidents/", json={
        "title": "Comments Test", "description": "Test comments",
        "urgency": 2, "impact": 2,
    })
    inc_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/v1/incidents/{inc_id}/comments",
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_add_comment(client: AsyncClient, _auth_token: str):
    create_resp = await client.post("/api/v1/incidents/", json={
        "title": "Add Comment", "description": "Test adding comment",
        "urgency": 2, "impact": 2,
    })
    inc_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/v1/incidents/{inc_id}/comments",
        json={"content": "This is a test comment", "is_internal": False},
        headers={"Authorization": f"Bearer {_auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "This is a test comment"
    assert data["is_internal"] is False
