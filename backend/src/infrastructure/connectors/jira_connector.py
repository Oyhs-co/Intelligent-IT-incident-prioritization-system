"""Conector para Jira."""

from __future__ import annotations

from typing import Any, Optional
import aiohttp

from .base_connector import (
    BaseTicketConnector,
    ExternalTicket,
    TicketConnectionError,
    TicketSyncError,
    SyncDirection,
)
from src.shared.logging import get_logger

logger = get_logger("connectors.jira")


class JiraConnector(BaseTicketConnector):
    """Conector para Jira Cloud/Server."""

    def __init__(
        self,
        base_url: str,
        api_token: str,
        username: str,
        project_key: str = "ITSM",
    ):
        super().__init__(base_url, api_token, username)
        self._project_key = project_key
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def connect(self) -> bool:
        """Establece conexión con Jira."""
        try:
            auth = aiohttp.BasicAuth(self._username, self._api_token)
            self._session = aiohttp.ClientSession(
                auth=auth,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            )

            url = f"{self._base_url}/rest/api/3/myself"
            async with self._session.get(url) as response:
                if response.status == 200:
                    self._connected = True
                    logger.info("Connected to Jira successfully")
                    return True
                else:
                    raise TicketConnectionError(f"Jira auth failed: {response.status}")

        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to Jira: {e}")
            raise TicketConnectionError(f"Jira connection failed: {e}")

    async def disconnect(self) -> None:
        """Cierra la conexión."""
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False
        logger.info("Disconnected from Jira")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Garantiza que la sesión existe."""
        if not self._session or self._session.closed:
            await self.connect()
        return self._session

    async def get_ticket(self, ticket_id: str) -> ExternalTicket:
        """Obtiene un ticket de Jira."""
        session = await self._ensure_session()
        url = f"{self._base_url}/rest/api/3/issue/{ticket_id}"

        try:
            async with session.get(url) as response:
                if response.status == 404:
                    raise TicketSyncError(f"Ticket {ticket_id} not found in Jira")

                if response.status != 200:
                    raise TicketSyncError(f"Jira API error: {response.status}")

                data = await response.json()
                return self._parse_jira_issue(data)

        except aiohttp.ClientError as e:
            logger.error(f"Failed to get Jira ticket: {e}")
            raise TicketSyncError(f"Failed to get ticket: {e}")

    async def list_tickets(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ExternalTicket]:
        """Lista tickets de Jira."""
        session = await self._ensure_session()

        jql_parts = [f"project = {self._project_key}"]
        if status:
            jql_parts.append(f"status = '{status}'")
        jql = " AND ".join(jql_parts)

        url = f"{self._base_url}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": limit,
            "startAt": offset,
            "fields": "summary,description,status,priority,created,updated,assignee,reporter",
        }

        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise TicketSyncError(f"Jira search failed: {response.status}")

                data = await response.json()
                return [self._parse_jira_issue(issue) for issue in data.get("issues", [])]

        except aiohttp.ClientError as e:
            logger.error(f"Failed to list Jira tickets: {e}")
            raise TicketSyncError(f"Failed to list tickets: {e}")

    async def create_ticket(
        self,
        title: str,
        description: str,
        priority: Optional[int] = None,
        category: Optional[str] = None,
        **kwargs,
    ) -> ExternalTicket:
        """Crea un ticket en Jira."""
        session = await self._ensure_session()
        url = f"{self._base_url}/rest/api/3/issue"

        priority_map = {1: "Highest", 2: "High", 3: "Medium", 4: "Low"}

        payload = {
            "fields": {
                "project": {"key": self._project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}],
                        }
                    ],
                },
                "issuetype": {"name": "Task"},
            }
        }

        if priority and priority in priority_map:
            payload["fields"]["priority"] = {"name": priority_map[priority]}

        try:
            async with session.post(url, json=payload) as response:
                if response.status not in (200, 201):
                    text = await response.text()
                    raise TicketSyncError(f"Failed to create ticket: {text}")

                data = await response.json()
                return await self.get_ticket(data["key"])

        except aiohttp.ClientError as e:
            logger.error(f"Failed to create Jira ticket: {e}")
            raise TicketSyncError(f"Failed to create ticket: {e}")

    async def update_ticket(
        self,
        ticket_id: str,
        **updates,
    ) -> ExternalTicket:
        """Actualiza un ticket en Jira."""
        session = await self._ensure_session()
        url = f"{self._base_url}/rest/api/3/issue/{ticket_id}"

        payload = {"fields": {}}

        if "title" in updates:
            payload["fields"]["summary"] = updates["title"]
        if "description" in updates:
            payload["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": updates["description"]}],
                    }
                ],
            }
        if "status" in updates:
            payload["fields"]["status"] = {"name": updates["status"]}

        try:
            async with session.put(url, json=payload) as response:
                if response.status not in (200, 204):
                    raise TicketSyncError(f"Failed to update ticket: {response.status}")

                return await self.get_ticket(ticket_id)

        except aiohttp.ClientError as e:
            logger.error(f"Failed to update Jira ticket: {e}")
            raise TicketSyncError(f"Failed to update ticket: {e}")

    async def sync_ticket(
        self,
        internal_incident_id: str,
        external_ticket_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
    ) -> dict[str, Any]:
        """Sincroniza un ticket entre sistemas."""
        logger.info(
            "Syncing ticket",
            internal_id=internal_incident_id,
            external_id=external_ticket_id,
            direction=direction.value,
        )

        try:
            external_ticket = await self.get_ticket(external_ticket_id)

            return {
                "success": True,
                "external_ticket": {
                    "id": external_ticket.external_id,
                    "title": external_ticket.title,
                    "status": external_ticket.status,
                    "priority": external_ticket.priority,
                },
                "sync_direction": direction.value,
            }

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise TicketSyncError(f"Sync failed: {e}")

    def _parse_jira_issue(self, data: dict) -> ExternalTicket:
        """Convierte un issue de Jira a ExternalTicket."""
        fields = data.get("fields", {})

        return ExternalTicket(
            external_id=data.get("key"),
            external_system="jira",
            title=fields.get("summary", ""),
            description=self._extract_description(fields.get("description")),
            status=fields.get("status", {}).get("name", "Unknown"),
            priority=self._map_priority(fields.get("priority")),
            category=None,
            created_at=fields.get("created"),
            updated_at=fields.get("updated"),
            assignee=fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            reporter=fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
            metadata={"issue_type": fields.get("issuetype", {}).get("name")},
        )

    def _extract_description(self, description: Any) -> str:
        """Extrae texto de la descripción de Jira."""
        if not description:
            return ""
        if isinstance(description, str):
            return description
        if isinstance(description, dict):
            content = description.get("content", [])
            parts = []
            for block in content:
                if isinstance(block, dict) and "content" in block:
                    for item in block["content"]:
                        if item.get("type") == "text":
                            parts.append(item.get("text", ""))
            return " ".join(parts)
        return str(description)

    def _map_priority(self, priority: Any) -> Optional[int]:
        """Mapea la prioridad de Jira a número."""
        if not priority:
            return None
        name = priority.get("name", "").lower()
        mapping = {"highest": 1, "high": 2, "medium": 3, "low": 4, "lowest": 4}
        return mapping.get(name, 3)
