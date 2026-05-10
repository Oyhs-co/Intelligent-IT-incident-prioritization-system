"""Servicio de métricas para Prometheus."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

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

    def __post_init__(self) -> None:
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

    def __post_init__(self) -> None:
        self.confidence_distribution = {}


class MetricsService:
    """Servicio para recolectar y calcular métricas usando consultas agregadas."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_overview_metrics(self) -> OverviewMetrics:
        """Obtiene métricas generales del sistema usando consultas agregadas."""
        from src.infrastructure.database.models import IncidentModel, UserModel

        metrics = OverviewMetrics()
        now = datetime.now(UTC)

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - __import__("datetime").timedelta(days=7)
        month_start = today_start - __import__("datetime").timedelta(days=30)

        stmt_total = select(func.count(IncidentModel.id))
        result = await self._session.execute(stmt_total)
        total = result.scalar() or 0
        stmt_counts = select(
            func.sum(case((IncidentModel.created_at >= today_start, 1), else_=0)).label("today"),
            func.sum(case((IncidentModel.created_at >= week_start, 1), else_=0)).label("week"),
            func.sum(case((IncidentModel.created_at >= month_start, 1), else_=0)).label("month"),
            func.sum(case((IncidentModel.status == "open", 1), else_=0)).label("open"),
            func.sum(case((IncidentModel.status == "in_progress", 1), else_=0)).label("in_progress"),
            func.sum(case((IncidentModel.status == "resolved", 1), else_=0)).label("resolved"),
            func.sum(case((IncidentModel.status == "closed", 1), else_=0)).label("closed"),
            func.sum(case(
                (IncidentModel.sla_deadline.isnot(None), 1),
                else_=0,
            )).label("has_sla"),
            func.sum(case(
                (
                    IncidentModel.sla_deadline.isnot(None),
                    case((now > IncidentModel.sla_deadline, 1), else_=0),
                ),
                else_=0,
            )).label("sla_breach"),
            func.sum(case(
                (
                    IncidentModel.confidence_score.isnot(None),
                    case((IncidentModel.created_at >= today_start, 1), else_=0),
                ),
                else_=0,
            )).label("ai_today"),
        ).select_from(IncidentModel)

        result = await self._session.execute(stmt_counts)
        row = result.one()

        metrics.total_incidents_today = row.today or 0
        metrics.total_incidents_week = row.week or 0
        metrics.total_incidents_month = row.month or 0
        metrics.incidents_open = row.open or 0
        metrics.incidents_in_progress = row.in_progress or 0
        metrics.incidents_resolved = row.resolved or 0
        metrics.incidents_closed = row.closed or 0
        metrics.sla_breach_count = row.sla_breach or 0

        if total:
            metrics.sla_compliance_rate = (total - metrics.sla_breach_count) / total * 100

        stmt_resolution = select(
            IncidentModel.resolved_at,
            IncidentModel.created_at,
        ).where(
            IncidentModel.status.in_(["resolved", "closed"]),
            IncidentModel.resolved_at.isnot(None),
            IncidentModel.created_at.isnot(None),
        )
        result = await self._session.execute(stmt_resolution)
        resolved_with_time = result.all()

        if resolved_with_time:
            total_minutes = sum(
                (r.resolved_at - r.created_at).total_seconds() / 60
                for r in resolved_with_time
            )
            metrics.avg_resolution_time_minutes = total_minutes / len(resolved_with_time)

        stmt_avg_conf = select(func.avg(IncidentModel.confidence_score)).where(
            IncidentModel.confidence_score.isnot(None),
        )
        result = await self._session.execute(stmt_avg_conf)
        avg_conf = result.scalar()
        if avg_conf:
            metrics.model_confidence_avg = float(avg_conf)

        metrics.ai_predictions_today = row.ai_today or 0

        stmt_users = select(func.count(UserModel.id)).where(UserModel.is_active)
        result = await self._session.execute(stmt_users)
        metrics.active_users = result.scalar() or 0

        stmt_techs = select(func.count(UserModel.id)).where(
            UserModel.is_active.is_(True),
            UserModel.role == "technician",
        )
        result = await self._session.execute(stmt_techs)
        metrics.active_technicians = result.scalar() or 0

        logger.info("Métricas generales calculadas", total_incidentes=total)

        return metrics

    async def get_incident_metrics(self) -> IncidentMetrics:
        """Obtiene métricas detalladas de incidentes usando group_by."""
        from src.infrastructure.database.models import IncidentModel

        metrics = IncidentMetrics()

        stmt_status = select(
            IncidentModel.status,
            func.count(IncidentModel.id),
        ).group_by(IncidentModel.status)
        result = await self._session.execute(stmt_status)
        for status, count in result:
            metrics.by_status[status] = count

        stmt_priority = select(
            IncidentModel.priority,
            func.count(IncidentModel.id),
        ).where(IncidentModel.priority.isnot(None)).group_by(IncidentModel.priority)
        result = await self._session.execute(stmt_priority)
        for priority, count in result:
            metrics.by_priority[priority] = count

        stmt_category = select(
            IncidentModel.category,
            func.count(IncidentModel.id),
        ).where(IncidentModel.category.isnot(None)).group_by(IncidentModel.category)
        result = await self._session.execute(stmt_category)
        for category, count in result:
            metrics.by_category[category] = count

        logger.info("Métricas de incidentes calculadas")

        return metrics

    async def get_ai_metrics(self) -> AIMetrics:
        """Obtiene métricas de IA/ML usando consultas agregadas."""
        from src.infrastructure.database.models import IncidentModel

        metrics = AIMetrics()

        stmt_count = select(func.count(IncidentModel.id)).where(
            IncidentModel.confidence_score.isnot(None),
        )
        result = await self._session.execute(stmt_count)
        metrics.total_predictions = result.scalar() or 0

        if metrics.total_predictions:
            stmt_avg = select(func.avg(IncidentModel.confidence_score)).where(
                IncidentModel.confidence_score.isnot(None),
            )
            result = await self._session.execute(stmt_avg)
            avg = result.scalar()
            if avg:
                metrics.avg_confidence = float(avg)

            stmt_dist = select(
                func.sum(case((IncidentModel.confidence_score >= 0.8, 1), else_=0)).label("high"),
                func.sum(case(
                    (IncidentModel.confidence_score >= 0.5, 1),
                    else_=0,
                )).label("med_raw"),
                func.sum(case((IncidentModel.confidence_score < 0.5, 1), else_=0)).label("low"),
            ).where(IncidentModel.confidence_score.isnot(None))
            result = await self._session.execute(stmt_dist)
            row = result.one()

            high = row.high or 0
            med = (row.med_raw or 0) - high
            low = row.low or 0

            metrics.confidence_distribution = {
                "high": max(0, high),
                "medium": max(0, med),
                "low": max(0, low),
            }

        logger.info("Métricas IA calculadas", total_predicciones=metrics.total_predictions)

        return metrics
