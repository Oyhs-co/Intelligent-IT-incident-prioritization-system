"""Servicio de métricas para Prometheus."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.logging import get_logger

if TYPE_CHECKING:
    from src.infrastructure.database.models import IncidentModel, UserModel, MetricModel

logger = get_logger("metrics_service")


@dataclass
class OverviewMetrics:
    """Métricas generales del sistema."""

    total_incidents_today: int = 0
    total_incidents_week: int = 0
    total_incidents_month: int = 0
    incidents_open: int = 0
    incidents_in_progress: int = 0
    incidents_resolved: int = 0
    incidents_closed: int = 0
    avg_response_time_minutes: float = 0.0
    avg_resolution_time_minutes: float = 0.0
    sla_compliance_rate: float = 0.0
    sla_breach_count: int = 0
    model_accuracy: float = 0.0
    model_confidence_avg: float = 0.0
    ai_predictions_today: int = 0
    active_users: int = 0
    active_technicians: int = 0


@dataclass
class IncidentMetrics:
    """Métricas detalladas de incidentes."""

    by_status: dict = None
    by_priority: dict = None
    by_category: dict = None
    avg_age_by_priority: dict = None
    resolution_rate_by_priority: dict = None

    def __post_init__(self):
        self.by_status = {}
        self.by_priority = {}
        self.by_category = {}
        self.avg_age_by_priority = {}
        self.resolution_rate_by_priority = {}


@dataclass
class AIMetrics:
    """Métricas de IA/ML."""

    total_predictions: int = 0
    accuracy: float = 0.0
    avg_confidence: float = 0.0
    avg_latency_ms: float = 0.0
    confidence_distribution: dict = None

    def __post_init__(self):
        self.confidence_distribution = {}


class MetricsService:
    """Servicio para recolectar y calcular métricas."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_overview_metrics(self) -> OverviewMetrics:
        """Obtiene métricas generales del sistema."""
        from src.infrastructure.database.models import IncidentModel, UserModel

        metrics = OverviewMetrics()
        now = datetime.utcnow()

        stmt_incidents = select(IncidentModel)
        result = await self._session.execute(stmt_incidents)
        incidents = result.scalars().all()

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)

        metrics.total_incidents_today = sum(1 for i in incidents if i.created_at >= today_start)
        metrics.total_incidents_week = sum(1 for i in incidents if i.created_at >= week_start)
        metrics.total_incidents_month = sum(1 for i in incidents if i.created_at >= month_start)

        metrics.incidents_open = sum(1 for i in incidents if i.status == "open")
        metrics.incidents_in_progress = sum(1 for i in incidents if i.status == "in_progress")
        metrics.incidents_resolved = sum(1 for i in incidents if i.status == "resolved")
        metrics.incidents_closed = sum(1 for i in incidents if i.status == "closed")

        resolved_with_time = [
            i for i in incidents
            if i.status in ("resolved", "closed") and i.resolved_at and i.created_at
        ]
        if resolved_with_time:
            total_time = sum(
                (i.resolved_at - i.created_at).total_seconds() / 60
                for i in resolved_with_time
            )
            metrics.avg_resolution_time_minutes = total_time / len(resolved_with_time)

        breached = sum(1 for i in incidents if i.sla_deadline and now > i.sla_deadline and i.status not in ("resolved", "closed"))
        metrics.sla_breach_count = breached
        if incidents:
            metrics.sla_compliance_rate = (len(incidents) - breached) / len(incidents) * 100

        priorities_with_confidence = [i for i in incidents if i.confidence_score]
        if priorities_with_confidence:
            metrics.model_confidence_avg = sum(i.confidence_score for i in priorities_with_confidence) / len(priorities_with_confidence)

        metrics.ai_predictions_today = sum(
            1 for i in incidents
            if i.confidence_score and i.created_at >= today_start
        )

        stmt_users = select(UserModel).where(UserModel.is_active == True)
        result = await self._session.execute(stmt_users)
        users = result.scalars().all()
        metrics.active_users = len(users)
        metrics.active_technicians = len([u for u in users if u.role == "technician"])

        logger.info("Overview metrics calculated", total_incidents=len(incidents))

        return metrics

    async def get_incident_metrics(self) -> IncidentMetrics:
        """Obtiene métricas detalladas de incidentes."""
        from src.infrastructure.database.models import IncidentModel

        metrics = IncidentMetrics()
        stmt = select(IncidentModel)
        result = await self._session.execute(stmt)
        incidents = result.scalars().all()

        for incident in incidents:
            metrics.by_status[incident.status] = metrics.by_status.get(incident.status, 0) + 1
            if incident.category:
                metrics.by_category[incident.category] = metrics.by_category.get(incident.category, 0) + 1
            if incident.priority:
                metrics.by_priority[incident.priority] = metrics.by_priority.get(incident.priority, 0) + 1

        logger.info("Incident metrics calculated")

        return metrics

    async def get_ai_metrics(self) -> AIMetrics:
        """Obtiene métricas de IA/ML."""
        from src.infrastructure.database.models import IncidentModel

        metrics = AIMetrics()
        stmt = select(IncidentModel).where(IncidentModel.confidence_score.isnot(None))
        result = await self._session.execute(stmt)
        incidents = result.scalars().all()

        metrics.total_predictions = len(incidents)

        if incidents:
            metrics.avg_confidence = sum(i.confidence_score for i in incidents) / len(incidents)

            high_conf = sum(1 for i in incidents if i.confidence_score >= 0.8)
            med_conf = sum(1 for i in incidents if 0.5 <= i.confidence_score < 0.8)
            low_conf = sum(1 for i in incidents if i.confidence_score < 0.5)

            metrics.confidence_distribution = {
                "high": high_conf,
                "medium": med_conf,
                "low": low_conf,
            }

        logger.info("AI metrics calculated", total_predictions=metrics.total_predictions)

        return metrics
