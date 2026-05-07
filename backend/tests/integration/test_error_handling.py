"""Tests de integración para exception handlers globales."""

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import AsyncClient, ASGITransport

from src.shared.exceptions import (
    NotFoundException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    DatabaseException,
    AIServiceException,
)


def _make_app_with_route(exception_cls, detail="Test error", resource=None):
    """Crea una app efímera con una ruta que lanza una excepción específica."""
    from src.presentation.api.app import _add_exception_handlers

    app = FastAPI()

    # NotFoundException requires two args: resource name and identifier
    if exception_cls is NotFoundException:
        exc = exception_cls(resource or "Resource", detail)
    elif resource:
        exc = exception_cls(detail, resource)
    else:
        exc = exception_cls(detail)

    @app.get("/raise-error")
    async def raise_error():
        raise exc

    _add_exception_handlers(app)
    return app


@pytest.mark.asyncio
@pytest.mark.parametrize("exception_cls,expected_status,expected_code", [
    (NotFoundException, 404, "RESOURCE_NOT_FOUND"),
    (ValidationException, 400, "VALIDATION_ERROR"),
    (AuthenticationException, 401, "AUTH_ERROR"),
    (AuthorizationException, 403, "AUTHORIZATION_ERROR"),
    (ConflictException, 409, "CONFLICT"),
    (DatabaseException, 500, "DB_ERROR"),
    (AIServiceException, 503, "AI_ERROR"),
])
async def test_exception_handler_returns_expected_status(
    exception_cls, expected_status, expected_code,
):
    """Cada exception handler debe retornar el status code correcto."""
    app = _make_app_with_route(exception_cls, detail="test-123")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/raise-error")
        assert response.status_code == expected_status

        data = response.json()
        assert "error" in data
        assert "detail" in data


@pytest.mark.asyncio
async def test_not_found_with_resource():
    """NotFoundException debe incluir el nombre del recurso en el detalle."""
    app = _make_app_with_route(
        NotFoundException, detail="abc-123", resource="Incident"
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/raise-error")
        assert response.status_code == 404
        data = response.json()
        assert "Incident" in data["detail"]
        assert "abc-123" in data["detail"]


@pytest.mark.asyncio
async def test_database_exception_hides_detail():
    """DatabaseException no debe exponer detalles internos."""
    app = _make_app_with_route(DatabaseException, detail="Internal connection timeout")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/raise-error")
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "A database error occurred"


def test_exception_handlers_registered():
    """Verifica que todos los exception handlers estén registrados en el app real."""
    from src.presentation.api.app import app
    from src.shared.exceptions import (
        NotFoundException, ValidationException, AuthenticationException,
        AuthorizationException, ConflictException, DatabaseException, AIServiceException,
    )

    for exc_cls in [NotFoundException, ValidationException, AuthenticationException,
                    AuthorizationException, ConflictException, DatabaseException,
                    AIServiceException]:
        assert exc_cls in app.exception_handlers, f"{exc_cls.__name__} not registered"

    assert Exception in app.exception_handlers, "Exception handler not registered"


@pytest.mark.asyncio
async def test_validation_error_through_real_app(client):
    """Verifica que 400/422 funcione a través del app real."""
    response = await client.post("/api/v1/incidents/", json={"title": "", "description": ""})
    assert response.status_code in (400, 422)
    data = response.json()
    assert "detail" in data or "error" in data
