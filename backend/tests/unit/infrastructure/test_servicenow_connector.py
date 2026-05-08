"""Tests unitarios para ServiceNowConnector."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.connectors.base_connector import (
    ExternalTicket,
    SyncDirection,
    TicketConnectionError,
    TicketSyncError,
)
from src.infrastructure.connectors.servicenow_connector import ServiceNowConnector


def _make_response(status: int, json_data: dict | None = None):
    mock = AsyncMock(spec_set=["status", "json"])
    mock.status = status
    if json_data is not None:
        mock.json = AsyncMock(return_value=json_data)
    return mock


def _make_get_context_manager(response_mock):
    cm = AsyncMock()
    cm.__aenter__.return_value = response_mock
    cm.__aexit__.return_value = None
    return cm


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.get.return_value = _make_get_context_manager(_make_response(200))
    session.post.return_value = _make_get_context_manager(_make_response(201))
    session.patch.return_value = _make_get_context_manager(_make_response(200))
    session.closed = False
    return session


@pytest.fixture
def connector():
    return ServiceNowConnector(
        base_url="https://dev12345.service-now.com",
        api_token="token-456",
        username="admin",
        instance_name="dev12345",
    )


class TestServiceNowConnector:
    """Tests para ServiceNowConnector."""

    @pytest.mark.asyncio
    async def test_connect_success(self, connector, mock_session):
        """Conexión exitosa debe retornar True."""
        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {"result": []}),
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with patch("aiohttp.BasicAuth", return_value=MagicMock()):
                result = await connector.connect()

        assert result is True
        assert connector._connected is True

    @pytest.mark.asyncio
    async def test_connect_unauthorized(self, connector, mock_session):
        """Conexión con 401 debe lanzar TicketConnectionError."""
        mock_session.get.return_value = _make_get_context_manager(
            _make_response(401),
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with patch("aiohttp.BasicAuth", return_value=MagicMock()):
                with pytest.raises(TicketConnectionError, match="auth failed"):
                    await connector.connect()

    @pytest.mark.asyncio
    async def test_connect_api_error(self, connector, mock_session):
        """Conexión con error HTTP debe lanzar TicketConnectionError."""
        mock_session.get.return_value = _make_get_context_manager(
            _make_response(500),
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with patch("aiohttp.BasicAuth", return_value=MagicMock()):
                with pytest.raises(TicketConnectionError):
                    await connector.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, connector):
        """Disconnect debe cerrar sesión."""
        session = AsyncMock()
        connector._session = session
        connector._connected = True

        await connector.disconnect()

        assert connector._connected is False
        assert connector._session is None
        session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, connector):
        """Health check healthy."""
        connector.connect = AsyncMock(return_value=True)
        result = await connector.health_check()
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, connector):
        """Health check unhealthy."""
        connector.connect = AsyncMock(side_effect=Exception("Fail"))
        result = await connector.health_check()
        assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_get_ticket_success(self, connector, mock_session):
        """get_ticket debe parsear respuesta SNOW correctamente."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "result": {
                    "number": "INC001",
                    "short_description": "Server down",
                    "description": "Critical server outage",
                    "state": "2",
                    "priority": "1",
                    "category": "infrastructure",
                    "sys_created_on": "2024-01-01",
                    "sys_updated_on": "2024-01-02",
                    "assigned_to": {"display_value": "John Doe"},
                    "caller_id": {"display_value": "Jane Doe"},
                    "sys_id": "sys001",
                    "impact": "3",
                    "urgency": "2",
                },
            }),
        )

        ticket = await connector.get_ticket("INC001")

        assert isinstance(ticket, ExternalTicket)
        assert ticket.external_id == "INC001"
        assert ticket.title == "Server down"
        assert ticket.status == "in_progress"
        assert ticket.priority == 1
        assert ticket.assignee == "John Doe"
        assert ticket.reporter == "Jane Doe"

    @pytest.mark.asyncio
    async def test_get_ticket_not_found(self, connector, mock_session):
        """get_ticket con 404 debe lanzar error."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(404),
        )

        with pytest.raises(TicketSyncError, match="not found"):
            await connector.get_ticket("INC999")

    @pytest.mark.asyncio
    async def test_list_tickets_success(self, connector, mock_session):
        """list_tickets debe retornar lista de tickets."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "result": [
                    {
                        "number": "INC001",
                        "short_description": "Issue one",
                        "description": "Desc one",
                        "state": "1",
                        "priority": "2",
                        "category": "network",
                    },
                    {
                        "number": "INC002",
                        "short_description": "Issue two",
                        "description": "Desc two",
                        "state": "7",
                        "priority": "3",
                        "category": "software",
                    },
                ],
            }),
        )

        tickets = await connector.list_tickets()

        assert len(tickets) == 2
        assert tickets[0].external_id == "INC001"
        assert tickets[0].status == "open"
        assert tickets[1].status == "closed"

    @pytest.mark.asyncio
    async def test_list_tickets_with_status_filter(self, connector, mock_session):
        """list_tickets con filtro status debe mapear estado."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {"result": []}),
        )

        await connector.list_tickets(status="in_progress")

        call_params = mock_session.get.call_args[1]["params"]
        assert call_params["state"] == 2

    @pytest.mark.asyncio
    async def test_list_tickets_empty(self, connector, mock_session):
        """list_tickets sin resultados debe retornar []."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {"result": []}),
        )

        tickets = await connector.list_tickets()
        assert tickets == []

    @pytest.mark.asyncio
    async def test_create_ticket(self, connector, mock_session):
        """create_ticket debe crear y retornar ticket."""
        connector._session = mock_session
        connector._connected = True

        mock_session.post.return_value = _make_get_context_manager(
            _make_response(201, {
                "result": {
                    "number": "INC003",
                    "short_description": "New issue",
                    "description": "New description",
                    "state": "1",
                    "priority": "2",
                    "category": "network",
                },
            }),
        )

        ticket = await connector.create_ticket(
            title="New issue",
            description="New description",
            priority=2,
            category="network",
        )

        assert ticket.external_id == "INC003"
        assert ticket.title == "New issue"
        assert ticket.priority == 2

    @pytest.mark.asyncio
    async def test_create_ticket_failure(self, connector, mock_session):
        """create_ticket con error debe lanzar TicketSyncError."""
        connector._session = mock_session
        connector._connected = True

        mock_resp = AsyncMock()
        mock_resp.status = 400
        mock_resp.text = AsyncMock(return_value="Bad request")

        mock_session.post.return_value = _make_get_context_manager(mock_resp)

        with pytest.raises(TicketSyncError):
            await connector.create_ticket(title="Bad", description="Bad")

    @pytest.mark.asyncio
    async def test_update_ticket(self, connector, mock_session):
        """update_ticket debe actualizar y retornar ticket."""
        connector._session = mock_session
        connector._connected = True

        mock_session.patch.return_value = _make_get_context_manager(
            _make_response(200),
        )

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "result": {
                    "number": "INC001",
                    "short_description": "Updated title",
                    "description": "Updated desc",
                    "state": "6",
                    "priority": "1",
                },
            }),
        )

        ticket = await connector.update_ticket(
            "INC001",
            title="Updated title",
            status="resolved",
        )

        assert ticket.title == "Updated title"
        assert ticket.status == "resolved"

    @pytest.mark.asyncio
    async def test_sync_ticket(self, connector, mock_session):
        """sync_ticket debe retornar resultado."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "result": {
                    "number": "INC001",
                    "short_description": "Synced",
                    "description": "Synced desc",
                    "state": "1",
                    "priority": "2",
                },
            }),
        )

        result = await connector.sync_ticket(
            internal_incident_id="INC-001",
            external_ticket_id="INC001",
            direction=SyncDirection.PUSH,
        )

        assert result["success"] is True
        assert result["external_ticket"]["id"] == "INC001"
        assert result["sync_direction"] == "push"

    def test_parse_snow_incident(self, connector):
        """_parse_snow_incident debe convertir datos SNOW a ExternalTicket."""
        data = {
            "number": "INC001",
            "short_description": "Test incident",
            "description": "Test description",
            "state": "6",
            "priority": "1",
            "category": "network",
            "sys_created_on": "2024-01-01",
            "sys_updated_on": "2024-01-02",
            "assigned_to": {"display_value": "Alice"},
            "caller_id": {"display_value": "Bob"},
            "sys_id": "sys001",
            "impact": "2",
            "urgency": "1",
        }

        ticket = connector._parse_snow_incident(data)

        assert ticket.external_id == "INC001"
        assert ticket.external_system == "servicenow"
        assert ticket.title == "Test incident"
        assert ticket.status == "resolved"
        assert ticket.priority == 1
        assert ticket.metadata["sys_id"] == "sys001"

    def test_parse_snow_incident_defaults(self, connector):
        """_parse_snow_incident con valores por defecto."""
        data = {
            "number": "INC002",
            "short_description": "Minimal",
            "state": "99",
            "priority": "invalid",
        }

        ticket = connector._parse_snow_incident(data)

        assert ticket.external_id == "INC002"
        assert ticket.status == "unknown"
        assert ticket.priority == 3

    def test_parse_snow_incident_no_assignee(self, connector):
        """_parse_snow_incident sin assignee debe ser None."""
        data = {
            "number": "INC003",
            "short_description": "No assignee",
            "state": "1",
            "priority": "3",
        }

        ticket = connector._parse_snow_incident(data)

        assert ticket.assignee is None
        assert ticket.reporter is None

    def test_is_connected(self, connector):
        """is_connected debe reflejar estado."""
        assert connector.is_connected() is False
        connector._connected = True
        assert connector.is_connected() is True
