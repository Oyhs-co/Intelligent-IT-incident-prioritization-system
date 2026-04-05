"""Caso de uso para obtener métricas generales del sistema."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import time

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.logging import get_logger

if TYPE_CHECKING:
    from src.infrastructure.database.models import IncidentModel, UserModel, MetricModel

logger = get_logger("use_cases.overview_metrics")


@dataclass
class OverviewMetricsResponse:
    """Respuesta de métricas generales."""

    total_incidents_today: int
    total_incidents_week: int
    total_incidents_month: int
    total_incidents_all_time: int
    incidents_open: int
    incidents_in_progress: int
    incidents_resolved: int
    incidents_closed: int
    incidents_pending: int
    avg_response_time_minutes: float
    avg_resolution_time_minutes: float
    avg_first_response_time_minutes: float
    sla_compliance_rate: float
    sla_breach_count: int
    model_predictions_today: int
    model_predictions_week: int
    model_avg_confidence: float
    active_users: int
    active_technicians: int
    priority_distribution: dict
    category_distribution: dict
    processing_time_ms: float


class GetOverviewMetricsUseCase:
    """Obtiene métricas generales del sistema."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(self) -> OverviewMetricsResponse:
        """Ejecuta la consulta de métricas."""
        start_time = time.time()

        logger.info("Calculating overview metrics")

        from src.infrastructure.database.models import IncidentModel, UserModel

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)

        stmt = select(IncidentModel)
        result = await self._session.execute(stmt)
        incidents = result.scalars().all()

        total_incidents_today = sum(1 for i in incidents if i.created_at >= today_start)
        total_incidents_week = sum(1 for i in incidents if i.created_at >= week_start)
        total_incidents_month = sum(1 for i in incidents if i.created_at >= month_start)

        incidents_open = sum(1 for i in incidents if i.status == "open")
        incidents_in_progress = sum(1 for i in incidents if i.status == "in_progress")
        incidents_resolved = sum(1 for i in incidents if i.status == "resolved")
        incidents_closed = sum(1 for i in incidents if i.status == "closed")
        incidents_pending = sum(1 for i in incidents if i.status == "pending")

        resolved_with_time = [
            i for i in incidents
            if i.status in ("resolved", "closed") and i.resolved_at and i.created_at
        ]
        avg_resolution_time = 0.0
        if resolved_with_time:
            total_time = sum(
                (i.resolved_at - i.created_at).total_seconds() / 60
                for i in resolved_with_time
            )
            avg_resolution_time = total_time / len(resolved_with_time)

        breached = sum(
            1 for i in incidents
            if i.sla_deadline and now > i.sla_deadline
            and i.status not in ("resolved", "closed")
        )
        sla_compliance = 0.0
        if incidents:
            sla_compliance = (len(incidents) - breached) / len(incidents) * 100

        predictions_today = sum(
            1 for i in incidents
            if i.confidence_score and i.created_at >= today_start
        )
        predictions_week = sum(
            1 for i in incidents
            if i.confidence_score and i.created_at >= week_start
        )

        priorities_with_confidence = [i for i in incidents if i.confidence_score]
        model_avg_confidence = 0.0
        if priorities_with_confidence:
            model_avg_confidence = sum(i.confidence_score for i in priorities_with_confidence) / len(priorities_with_confidence)

        priority_dist = {}
        for inc in incidents:
            p = inc.priority or "unclassified"
            priority_dist[p] = priority_dist.get(p, 0) + 1

        category_dist = {}
        for inc in incidents:
            if inc.category:
                category_dist[inc.category] = category_dist.get(inc.category, 0) + 1

        stmt_users = select(UserModel).where(UserModel.is_active == True)
        result_users = await self._session.execute(stmt_users)
        users = result_users.scalars().all()
        active_users = len(users)
        active_technicians = len([u for u in users if u.role == "technician"])

        processing_time = (time.time() - start_time) * 1000

        logger.log_system_metrics(
            total_incidents=len(incidents),
            active_incidents=incidents_open + incidents_in_progress,
            sla_compliance=sla_compliance,
        )

        return OverviewMetricsResponse(
            total_incidents_today=total_incidents_today,
            total_incidents_week=total_incidents_week,
            total_incidents_month=total_incidents_month,
            total_incidents_all_time=len(incidents),
            incidents_open=incidents_open,
            incidents_in_progress=incidents_in_progress,
            incidents_resolved=incidents_resolved,
            incidents_closed=incidents_closed,
            incidents_pending=incidents_pending,
            avg_response_time_minutes=0.0,
            avg_resolution_time_minutes=avg_resolution_time,
            avg_first_response_time_minutes=0.0,
            sla_compliance_rate=sla_compliance,
            sla_breach_count=breached,
            model_predictions_today=predictions_today,
            model_predictions_week=predictions_week,
            model_avg_confidence=model_avg_confidence,
            active_users=active_users,
            active_technicians=active_technicians,
            priority_distribution=priority_dist,
            category_distribution=category_dist,
            processing_time_ms=processing_time,
        )
