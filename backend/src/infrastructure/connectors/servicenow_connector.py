"""Conector para ServiceNow."""

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

logger = get_logger("connectors.servicenow")


class ServiceNowConnector(BaseTicketConnector):
    """Conector para ServiceNow."""

    def __init__(
        self,
        base_url: str,
        api_token: str,
        username: str,
        instance_name: str = "dev12345",
    ):
        super().__init__(base_url, api_token, username)
        self._instance_name = instance_name
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def connect(self) -> bool:
        """Establece conexión con ServiceNow."""
        try:
            auth = aiohttp.BasicAuth(self._username, self._api_token)
            self._session = aiohttp.ClientSession(
                auth=auth,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            )

            url = f"{self._base_url}/api/now/table/sys_user"
            params = {"sysparm_limit": 1}

            async with self._session.get(url, params=params) as response:
                if response.status == 200:
                    self._connected = True
                    logger.info("Connected to ServiceNow successfully")
                    return True
                elif response.status == 401:
                    raise TicketConnectionError("ServiceNow auth failed - check credentials")
                else:
                    raise TicketConnectionError(f"ServiceNow API error: {response.status}")

        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to ServiceNow: {e}")
            raise TicketConnectionError(f"ServiceNow connection failed: {e}")

    async def disconnect(self) -> None:
        """Cierra la conexión."""
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False
        logger.info("Disconnected from ServiceNow")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Garantiza que la sesión existe."""
        if not self._session or self._session.closed:
            await self.connect()
        return self._session

    async def get_ticket(self, ticket_id: str) -> ExternalTicket:
        """Obtiene un ticket de ServiceNow."""
        session = await self._ensure_session()
        url = f"{self._base_url}/api/now/table/incident/{ticket_id}"

        try:
            async with session.get(url) as response:
                if response.status == 404:
                    raise TicketSyncError(f"Ticket {ticket_id} not found in ServiceNow")

                if response.status != 200:
                    raise TicketSyncError(f"ServiceNow API error: {response.status}")

                data = await response.json()
                result = data.get("result", {})
                return self._parse_snow_incident(result)

        except aiohttp.ClientError as e:
            logger.error(f"Failed to get ServiceNow ticket: {e}")
            raise TicketSyncError(f"Failed to get ticket: {e}")

    async def list_tickets(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ExternalTicket]:
        """Lista tickets de ServiceNow."""
        session = await self._ensure_session()
        url = f"{self._base_url}/api/now/table/incident"

        params: dict[str, Any] = {
            "sysparm_limit": limit,
            "sysparm_offset": offset,
            "sysparm_fields": "number,short_description,description,state,priority,category,created,updated,assigned_to,caller_id",
        }

        if status:
            state_map = {"open": 1, "in_progress": 2, "resolved": 6, "closed": 7}
            params["state"] = state_map.get(status.lower(), 1)

        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise TicketSyncError(f"ServiceNow search failed: {response.status}")

                data = await response.json()
                return [self._parse_snow_incident(inc) for inc in data.get("result", [])]

        except aiohttp.ClientError as e:
            logger.error(f"Failed to list ServiceNow tickets: {e}")
            raise TicketSyncError(f"Failed to list tickets: {e}")

    async def create_ticket(
        self,
        title: str,
        description: str,
        priority: Optional[int] = None,
        category: Optional[str] = None,
        **kwargs,
    ) -> ExternalTicket:
        """Crea un ticket en ServiceNow."""
        session = await self._ensure_session()
        url = f"{self._base_url}/api/now/table/incident"

        payload: dict[str, Any] = {
            "short_description": title,
            "description": description,
        }

        if priority:
            payload["priority"] = str(priority)
        if category:
            payload["category"] = category

        try:
            async with session.post(url, json=payload) as response:
                if response.status not in (200, 201):
                    text = await response.text()
                    raise TicketSyncError(f"Failed to create ticket: {text}")

                data = await response.json()
                result = data.get("result", {})
                return self._parse_snow_incident(result)

        except aiohttp.ClientError as e:
            logger.error(f"Failed to create ServiceNow ticket: {e}")
            raise TicketSyncError(f"Failed to create ticket: {e}")

    async def update_ticket(
        self,
        ticket_id: str,
        **updates,
    ) -> ExternalTicket:
        """Actualiza un ticket en ServiceNow."""
        session = await self._ensure_session()
        url = f"{self._base_url}/api/now/table/incident/{ticket_id}"

        payload: dict[str, Any] = {}

        if "title" in updates:
            payload["short_description"] = updates["title"]
        if "description" in updates:
            payload["description"] = updates["description"]
        if "status" in updates:
            state_map = {"open": 1, "in_progress": 2, "resolved": 6, "closed": 7}
            payload["state"] = state_map.get(updates["status"].lower(), 1)

        try:
            async with session.patch(url, json=payload) as response:
                if response.status not in (200, 204):
                    raise TicketSyncError(f"Failed to update ticket: {response.status}")

                return await self.get_ticket(ticket_id)

        except aiohttp.ClientError as e:
            logger.error(f"Failed to update ServiceNow ticket: {e}")
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

    def _parse_snow_incident(self, data: dict) -> ExternalTicket:
        """Convierte un incident de ServiceNow a ExternalTicket."""
        priority_str = data.get("priority", "3")
        try:
            priority = int(priority_str)
        except (ValueError, TypeError):
            priority = 3

        state_str = data.get("state", "1")
        state_map = {1: "open", 2: "in_progress", 6: "resolved", 7: "closed"}
        status = state_map.get(int(state_str) if state_str else 1, "unknown")

        return ExternalTicket(
            external_id=data.get("number", ""),
            external_system="servicenow",
            title=data.get("short_description", ""),
            description=data.get("description", ""),
            status=status,
            priority=priority,
            category=data.get("category"),
            created_at=data.get("created_on") or data.get("sys_created_on"),
            updated_at=data.get("updated_on") or data.get("sys_updated_on"),
            assignee=data.get("assigned_to", {}).get("display_value") if isinstance(data.get("assigned_to"), dict) else data.get("assigned_to"),
            reporter=data.get("caller_id", {}).get("display_value") if isinstance(data.get("caller_id"), dict) else data.get("caller_id"),
            metadata={
                "sys_id": data.get("sys_id"),
                "impact": data.get("impact"),
                "urgency": data.get("urgency"),
            },
        )
