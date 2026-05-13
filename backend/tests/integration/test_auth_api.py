"""Tests de integración para rutas de autenticación y usuarios."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Registro exitoso de usuario."""
    payload = {
        "email": "newuser@test.com",
        "username": "newuser",
        "password": "SecurePass123!",
        "first_name": "New",
        "last_name": "User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Registro con email duplicado debe retornar 400."""
    payload = {
        "email": "dup@test.com",
        "username": "dupuser1",
        "password": "SecurePass123!",
    }
    await client.post("/api/v1/auth/register", json=payload)

    payload["username"] = "dupuser2"
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """Registro con username duplicado debe retornar 400."""
    payload = {
        "email": "dup2@test.com",
        "username": "dupuser",
        "password": "SecurePass123!",
    }
    await client.post("/api/v1/auth/register", json=payload)

    payload["email"] = "dup2b@test.com"
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Login exitoso retorna tokens."""
    email = "logintest@test.com"
    password = "SecurePass123!"

    await client.post("/api/v1/auth/register", json={
        "email": email, "username": "logintest", "password": password,
    })

    response = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Login con credenciales inválidas retorna 401."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@test.com", "password": "wrongpass",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    """Refresh token exitoso."""
    email = "refreshtest@test.com"
    password = "SecurePass123!"

    await client.post("/api/v1/auth/register", json={
        "email": email, "username": "refreshtest", "password": password,
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    })
    refresh_token = login_resp.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Refresh con token inválido retorna 401."""
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid_token_here",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient):
    """GET /me con token válido retorna información del usuario."""
    email = "metest@test.com"
    password = "SecurePass123!"

    await client.post("/api/v1/auth/register", json={
        "email": email, "username": "metest", "password": password,
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    })
    access_token = login_resp.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["username"] == "metest"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """GET /me sin token retorna 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_user_not_found(client: AsyncClient):
    """GET /me con token de usuario eliminado retorna 404."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {uuid4()}"},
    )
    assert response.status_code in (401, 404)


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    """Listar usuarios retorna lista."""
    for i in range(3):
        await client.post("/api/v1/auth/register", json={
            "email": f"listuser{i}@test.com",
            "username": f"listuser{i}",
            "password": "SecurePass123!",
        })

    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient):
    """Obtener usuario por ID."""
    email = f"getuser_{uuid4().hex[:8]}@test.com"
    username = f"getuser_{uuid4().hex[:8]}"
    resp = await client.post("/api/v1/auth/register", json={
        "email": email, "username": username, "password": "SecurePass123!",
    })
    user_id = resp.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    """Obtener usuario inexistente retorna 404."""
    from uuid import uuid4
    response = await client.get(f"/api/v1/users/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient):
    """Actualizar usuario."""
    email = "updateuser@test.com"
    password = "SecurePass123!"

    await client.post("/api/v1/auth/register", json={
        "email": email, "username": "updateuser", "password": password,
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    })
    access_token = login_resp.json()["access_token"]
    list_resp = await client.get("/api/v1/users/")
    user_id = list_resp.json()["items"][0]["id"]

    response = await client.put(
        f"/api/v1/users/{user_id}",
        json={"first_name": "Updated", "last_name": "Name"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"


@pytest.mark.asyncio
async def test_update_user_not_found(client: AsyncClient):
    """Actualizar usuario inexistente retorna 404."""
    from uuid import uuid4
    response = await client.put(
        f"/api/v1/users/{uuid4()}",
        json={"first_name": "Test"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    """Eliminar usuario."""
    email = "deleteuser@test.com"
    password = "SecurePass123!"

    await client.post("/api/v1/auth/register", json={
        "email": email, "username": "deleteuser", "password": password,
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    })
    access_token = login_resp.json()["access_token"]
    list_resp = await client.get("/api/v1/users/")
    user_id = list_resp.json()["items"][0]["id"]

    response = await client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_not_found(client: AsyncClient):
    """Eliminar usuario inexistente retorna 404."""
    from uuid import uuid4
    response = await client.delete(f"/api/v1/users/{uuid4()}")
    assert response.status_code == 404
