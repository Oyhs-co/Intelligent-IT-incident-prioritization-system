"""Tests unitarios para JiraConnector."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.connectors.base_connector import (
    ExternalTicket,
    SyncDirection,
    TicketConnectionError,
    TicketSyncError,
)
from src.infrastructure.connectors.jira_connector import JiraConnector


@pytest.fixture
def connector():
    return JiraConnector(
        base_url="https://jira.example.com",
        api_token="token-123",
        username="test-user",
        project_key="ITSM",
    )


def _make_response(status: int, json_data: dict | None = None):
    """Crea un mock de respuesta HTTP."""
    mock = AsyncMock(spec_set=["status", "json"])
    mock.status = status
    if json_data is not None:
        mock.json = AsyncMock(return_value=json_data)
    return mock


def _make_get_context_manager(response_mock):
    """Crea un async context manager para session.get()."""
    cm = AsyncMock()
    cm.__aenter__.return_value = response_mock
    cm.__aexit__.return_value = None
    return cm


@pytest.fixture
def mock_session():
    """Crea una sesión HTTP mockeada."""
    session = MagicMock()
    session.get.return_value = _make_get_context_manager(_make_response(200))
    session.post.return_value = _make_get_context_manager(_make_response(201))
    session.put.return_value = _make_get_context_manager(_make_response(204))
    session.patch.return_value = _make_get_context_manager(_make_response(200))
    session.closed = False
    return session


class TestJiraConnector:
    """Tests para JiraConnector."""

    @pytest.mark.asyncio
    async def test_connect_success(self, connector, mock_session):
        """Conexión exitosa debe retornar True y establecer _connected."""
        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {"key": "test"}),
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with patch("aiohttp.BasicAuth", return_value=MagicMock()):
                result = await connector.connect()

        assert result is True
        assert connector._connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self, connector, mock_session):
        """Fallo de conexión debe lanzar TicketConnectionError."""
        mock_session.get.return_value = _make_get_context_manager(
            _make_response(401),
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with patch("aiohttp.BasicAuth", return_value=MagicMock()):
                with pytest.raises(TicketConnectionError):
                    await connector.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, connector):
        """Disconnect debe cerrar sesión y marcar no conectado."""
        session = AsyncMock()
        connector._session = session
        connector._connected = True

        await connector.disconnect()

        assert connector._connected is False
        assert connector._session is None
        session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_no_session(self, connector):
        """Disconnect sin sesión no debe fallar."""
        connector._session = None
        await connector.disconnect()
        assert connector._connected is False

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, connector):
        """Health check debe retornar healthy cuando conecta."""
        async def _connect():
            connector._connected = True
            return True

        connector.connect = _connect
        result = await connector.health_check()

        assert result["status"] == "healthy"
        assert result["connected"] is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, connector):
        """Health check debe retornar unhealthy cuando falla."""
        connector.connect = AsyncMock(side_effect=Exception("Connection failed"))
        result = await connector.health_check()

        assert result["status"] == "unhealthy"
        assert result["connected"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_ticket_success(self, connector, mock_session):
        """get_ticket debe parsear respuesta Jira correctamente."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "key": "ITSM-42",
                "fields": {
                    "summary": "Server is down",
                    "description": {
                        "content": [
                            {"content": [{"type": "text", "text": "Critical outage"}]},
                        ],
                    },
                    "status": {"name": "In Progress"},
                    "priority": {"name": "Highest"},
                    "created": "2024-01-01",
                    "updated": "2024-01-02",
                    "assignee": {"displayName": "John Doe"},
                    "reporter": {"displayName": "Jane Doe"},
                    "issuetype": {"name": "Incident"},
                },
            }),
        )

        ticket = await connector.get_ticket("ITSM-42")

        assert isinstance(ticket, ExternalTicket)
        assert ticket.external_id == "ITSM-42"
        assert ticket.title == "Server is down"
        assert ticket.status == "In Progress"
        assert ticket.priority == 1
        assert ticket.assignee == "John Doe"
        assert ticket.reporter == "Jane Doe"

    @pytest.mark.asyncio
    async def test_get_ticket_not_found(self, connector, mock_session):
        """get_ticket con 404 debe lanzar TicketSyncError."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(404),
        )

        with pytest.raises(TicketSyncError, match="not found"):
            await connector.get_ticket("ITSM-999")

    @pytest.mark.asyncio
    async def test_get_ticket_api_error(self, connector, mock_session):
        """get_ticket con error HTTP debe lanzar TicketSyncError."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(500),
        )

        with pytest.raises(TicketSyncError):
            await connector.get_ticket("ITSM-42")

    @pytest.mark.asyncio
    async def test_list_tickets_success(self, connector, mock_session):
        """list_tickets debe retornar lista de ExternalTicket."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "issues": [
                    {
                        "key": "ITSM-1",
                        "fields": {
                            "summary": "Issue one",
                            "description": "Description one",
                            "status": {"name": "Open"},
                            "priority": {"name": "High"},
                            "created": "2024-01-01",
                            "updated": "2024-01-02",
                        },
                    },
                    {
                        "key": "ITSM-2",
                        "fields": {
                            "summary": "Issue two",
                            "description": "Description two",
                            "status": {"name": "Closed"},
                            "priority": None,
                            "created": "2024-01-03",
                            "updated": "2024-01-04",
                        },
                    },
                ],
            }),
        )

        tickets = await connector.list_tickets(status="Open", limit=10, offset=0)

        assert len(tickets) == 2
        assert tickets[0].external_id == "ITSM-1"
        assert tickets[1].external_id == "ITSM-2"
        assert tickets[0].priority == 2
        assert tickets[1].priority is None

    @pytest.mark.asyncio
    async def test_list_tickets_empty(self, connector, mock_session):
        """list_tickets sin resultados debe retornar lista vacía."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {"issues": []}),
        )

        tickets = await connector.list_tickets()
        assert tickets == []

    @pytest.mark.asyncio
    async def test_create_ticket(self, connector, mock_session):
        """create_ticket debe crear ticket y retornarlo."""
        connector._session = mock_session
        connector._connected = True

        mock_session.post.return_value = _make_get_context_manager(
            _make_response(201, {"key": "ITSM-100"}),
        )

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "key": "ITSM-100",
                "fields": {
                    "summary": "New issue",
                    "description": {"content": [{"content": [{"type": "text", "text": "Desc"}]}]},
                    "status": {"name": "Open"},
                    "priority": {"name": "Medium"},
                    "created": "2024-01-01",
                    "updated": "2024-01-02",
                },
            }),
        )

        ticket = await connector.create_ticket(
            title="New issue",
            description="Description of new issue",
            priority=3,
        )

        assert ticket.external_id == "ITSM-100"
        assert ticket.title == "New issue"

    @pytest.mark.asyncio
    async def test_update_ticket(self, connector, mock_session):
        """update_ticket debe actualizar y retornar ticket."""
        connector._session = mock_session
        connector._connected = True

        mock_session.put.return_value = _make_get_context_manager(
            _make_response(204),
        )

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "key": "ITSM-42",
                "fields": {
                    "summary": "Updated title",
                    "description": {"content": [{"content": [{"type": "text", "text": "Updated desc"}]}]},
                    "status": {"name": "Resolved"},
                    "priority": {"name": "Low"},
                    "created": "2024-01-01",
                    "updated": "2024-01-03",
                },
            }),
        )

        ticket = await connector.update_ticket(
            "ITSM-42",
            title="Updated title",
            status="Resolved",
        )

        assert ticket.title == "Updated title"
        assert ticket.status == "Resolved"

    @pytest.mark.asyncio
    async def test_update_ticket_failure(self, connector, mock_session):
        """update_ticket con error debe lanzar TicketSyncError."""
        connector._session = mock_session
        connector._connected = True

        mock_session.put.return_value = _make_get_context_manager(
            _make_response(400),
        )

        with pytest.raises(TicketSyncError):
            await connector.update_ticket("ITSM-42", title="Bad update")

    @pytest.mark.asyncio
    async def test_sync_ticket(self, connector, mock_session):
        """sync_ticket debe retornar resultado de sincronización."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(200, {
                "key": "ITSM-42",
                "fields": {
                    "summary": "Synced issue",
                    "description": {"content": [{"content": [{"type": "text", "text": "Synced"}]}]},
                    "status": {"name": "Open"},
                    "priority": {"name": "High"},
                    "created": "2024-01-01",
                    "updated": "2024-01-02",
                },
            }),
        )

        result = await connector.sync_ticket(
            internal_incident_id="INC-001",
            external_ticket_id="ITSM-42",
            direction=SyncDirection.PULL,
        )

        assert result["success"] is True
        assert result["external_ticket"]["id"] == "ITSM-42"
        assert result["sync_direction"] == "pull"

    @pytest.mark.asyncio
    async def test_sync_ticket_failure(self, connector, mock_session):
        """sync_ticket con error debe lanzar TicketSyncError."""
        connector._session = mock_session
        connector._connected = True

        mock_session.get.return_value = _make_get_context_manager(
            _make_response(404),
        )

        with pytest.raises(TicketSyncError):
            await connector.sync_ticket(
                internal_incident_id="INC-001",
                external_ticket_id="ITSM-999",
            )

    def test_parse_jira_issue(self, connector):
        """_parse_jira_issue debe convertir datos Jira a ExternalTicket."""
        data = {
            "key": "ITSM-1",
            "fields": {
                "summary": "Test issue",
                "description": "Plain text description",
                "status": {"name": "Open"},
                "priority": {"name": "Highest"},
                "created": "2024-01-01",
                "updated": "2024-01-02",
                "assignee": {"displayName": "Alice"},
                "reporter": {"displayName": "Bob"},
                "issuetype": {"name": "Bug"},
            },
        }

        ticket = connector._parse_jira_issue(data)

        assert ticket.external_id == "ITSM-1"
        assert ticket.external_system == "jira"
        assert ticket.title == "Test issue"
        assert ticket.status == "Open"
        assert ticket.priority == 1
        assert ticket.metadata["issue_type"] == "Bug"

    def test_parse_jira_issue_no_priority(self, connector):
        """_parse_jira_issue sin prioridad debe retornar None."""
        data = {
            "key": "ITSM-1",
            "fields": {
                "summary": "Test",
                "description": None,
                "status": {"name": "Open"},
                "priority": None,
            },
        }

        ticket = connector._parse_jira_issue(data)
        assert ticket.priority is None

    def test_map_priority(self, connector):
        """_map_priority debe mapear correctamente."""
        assert connector._map_priority({"name": "Highest"}) == 1
        assert connector._map_priority({"name": "High"}) == 2
        assert connector._map_priority({"name": "Medium"}) == 3
        assert connector._map_priority({"name": "Low"}) == 4
        assert connector._map_priority({"name": "Lowest"}) == 4
        assert connector._map_priority(None) is None
        assert connector._map_priority({}) is None

    def test_extract_description_dict(self, connector):
        """_extract_description con formato ADF debe extraer texto."""
        desc = {
            "content": [
                {"content": [{"type": "text", "text": "Hello"}, {"type": "text", "text": "World"}]},
            ],
        }
        result = connector._extract_description(desc)
        assert result == "Hello World"

    def test_extract_description_string(self, connector):
        """_extract_description con string debe retornarlo."""
        assert connector._extract_description("Plain text") == "Plain text"

    def test_extract_description_none(self, connector):
        """_extract_description con None debe retornar vacío."""
        assert connector._extract_description(None) == ""

    def test_is_connected(self, connector):
        """is_connected debe reflejar estado."""
        assert connector.is_connected() is False
        connector._connected = True
        assert connector.is_connected() is True
