"""Handlers para eventos de incidentes."""

from __future__ import annotations

from typing import Any

from .redis_publisher import EventChannel
from src.shared.logging import get_logger

logger = get_logger("event_handlers")


class IncidentEventHandler:
    """Manejador de eventos relacionados con incidentes."""

    def __init__(self, publisher=None):
        self._publisher = publisher

    async def on_incident_created(self, data: dict[str, Any]) -> None:
        """Handle para incidente creado."""
        logger.info(
            "Incident created event received",
            incident_id=data.get("incident_id"),
            ticket_number=data.get("ticket_number"),
        )

    async def on_incident_classified(self, data: dict[str, Any]) -> None:
        """Handle para incidente clasificado."""
        logger.info(
            "Incident classified event received",
            incident_id=data.get("incident_id"),
            priority=data.get("priority"),
            confidence=data.get("confidence"),
        )

    async def on_sla_alert(self, data: dict[str, Any]) -> None:
        """Handle para alerta SLA."""
        alert_type = data.get("alert_type", "unknown")
        logger.warning(
            f"SLA alert: {alert_type}",
            incident_id=data.get("incident_id"),
            ticket_number=data.get("ticket_number"),
            hours_remaining=data.get("hours_remaining"),
        )

    async def on_metrics_updated(self, data: dict[str, Any]) -> None:
        """Handle para métricas actualizadas."""
        logger.info(
            "Metrics updated event received",
            type=data.get("type"),
        )


class SLAWatcher:
    """Watcher para monitorear SLAs."""

    def __init__(self, publisher=None, check_interval: int = 300):
        self._publisher = publisher
        self._check_interval = check_interval
        self._running = False

    async def start(self) -> None:
        """Inicia el watcher."""
        self._running = True
        logger.info("SLA Watcher started")

    async def stop(self) -> None:
        """Detiene el watcher."""
        self._running = False
        logger.info("SLA Watcher stopped")

    async def check_sla_status(self) -> list[dict[str, Any]]:
        """Verifica estado de SLAs."""
        return []

    async def send_alerts(self, alerts: list[dict[str, Any]]) -> None:
        """Envía alertas de SLA."""
        if not self._publisher:
            return

        for alert in alerts:
            await self._publisher.publish_sla_alert(
                incident_id=alert["incident_id"],
                ticket_number=alert["ticket_number"],
                hours_remaining=alert["hours_remaining"],
                priority=alert["priority"],
            )
