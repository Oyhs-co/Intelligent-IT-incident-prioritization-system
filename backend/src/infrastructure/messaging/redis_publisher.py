"""Publicador Redis para eventos."""

from __future__ import annotations

import json
from typing import Any, Optional
from datetime import datetime
from enum import Enum

import redis.asyncio as redis

from src.shared.logging import get_logger

logger = get_logger("messaging.publisher")


class EventChannel(str, Enum):
    """Canales de eventos."""
    INCIDENTS_CREATED = "incidents:created"
    INCIDENTS_UPDATED = "incidents:updated"
    INCIDENTS_CLASSIFIED = "incidents:classified"
    INCIDENTS_ASSIGNED = "incidents:assigned"
    INCIDENTS_RESOLVED = "incidents:resolved"
    SLA_ALERTS = "sla:alerts"
    METRICS_UPDATED = "metrics:updated"
    AI_PREDICTIONS = "ai:predictions"


class RedisPublisher:
    """Publicador de eventos usando Redis Pub/Sub."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
    ):
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._client: Optional[redis.Redis] = None
        self._connected = False

    async def connect(self) -> None:
        """Establece conexión con Redis."""
        try:
            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                decode_responses=True,
            )
            await self._client.ping()
            self._connected = True
            logger.info("Connected to Redis publisher")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Cierra la conexión."""
        if self._client:
            await self._client.close()
        self._connected = False
        logger.info("Disconnected from Redis publisher")

    async def publish(
        self,
        channel: EventChannel,
        data: dict[str, Any],
        event_id: Optional[str] = None,
    ) -> int:
        """Publica un evento en un canal."""
        if not self._client:
            logger.warning("Redis not connected, skipping publish")
            return 0

        message = {
            "event_id": event_id or self._generate_event_id(),
            "channel": channel.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        try:
            subscribers = await self._client.publish(channel.value, json.dumps(message))
            logger.info(
                "Event published",
                channel=channel.value,
                event_id=message["event_id"],
                subscribers=subscribers,
            )
            return subscribers
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return 0

    async def publish_incident_created(
        self,
        incident_id: str,
        ticket_number: str,
        title: str,
        priority: Optional[int] = None,
    ) -> int:
        """Publica evento de incidente creado."""
        return await self.publish(
            EventChannel.INCIDENTS_CREATED,
            {
                "incident_id": incident_id,
                "ticket_number": ticket_number,
                "title": title,
                "priority": priority,
            },
        )

    async def publish_incident_classified(
        self,
        incident_id: str,
        ticket_number: str,
        priority: int,
        confidence: float,
        explanation: str,
    ) -> int:
        """Publica evento de clasificación."""
        return await self.publish(
            EventChannel.INCIDENTS_CLASSIFIED,
            {
                "incident_id": incident_id,
                "ticket_number": ticket_number,
                "priority": priority,
                "confidence": confidence,
                "explanation": explanation,
            },
        )

    async def publish_sla_alert(
        self,
        incident_id: str,
        ticket_number: str,
        hours_remaining: float,
        priority: int,
    ) -> int:
        """Publica alerta SLA."""
        return await self.publish(
            EventChannel.SLA_ALERTS,
            {
                "incident_id": incident_id,
                "ticket_number": ticket_number,
                "hours_remaining": hours_remaining,
                "priority": priority,
                "alert_type": "sla_warning" if hours_remaining > 0 else "sla_breach",
            },
        )

    async def publish_metrics_update(
        self,
        metrics_type: str,
        metrics_data: dict[str, Any],
    ) -> int:
        """Publica actualización de métricas."""
        return await self.publish(
            EventChannel.METRICS_UPDATED,
            {
                "type": metrics_type,
                "data": metrics_data,
            },
        )

    def _generate_event_id(self) -> str:
        """Genera ID único para el evento."""
        return f"{datetime.utcnow().timestamp()}"

    async def is_connected(self) -> bool:
        """Verifica si está conectado."""
        if not self._client:
            return False
        try:
            await self._client.ping()
            return True
        except Exception:
            return False
