"""Caso de uso para obtener métricas de SLA."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.sla_metrics")


@dataclass
class SLAByPriority:
    """Métricas SLA por prioridad."""

    priority: int
    priority_label: str
    total_incidents: int
    breached: int
    met: int
    compliance_rate: float
    avg_response_time_minutes: float
    avg_resolution_time_minutes: float


@dataclass
class SLAMetricsResponse:
    """Respuesta de métricas SLA."""

    overall_compliance_rate: float
    total_incidents: int
    breached_count: int
    met_count: int
    avg_resolution_time_minutes: float
    by_priority: list[SLAByPriority]
    at_risk_incidents: list[dict]
    processing_time_ms: float


class GetSLAMetricsUseCase:
    """Obtiene métricas de SLA."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(self) -> SLAMetricsResponse:
        """Ejecuta la consulta de métricas SLA."""
        start_time = time.time()

        logger.info("Calculating SLA metrics")

        from src.infrastructure.database.models import IncidentModel
        from src.domain.value_objects import PriorityLevel

        now = datetime.utcnow()

        stmt = select(IncidentModel)
        result = await self._session.execute(stmt)
        incidents = result.scalars().all()

        total = len(incidents)
        breached = 0
        met = 0
        total_resolution_time = 0.0
        resolved_count = 0
        at_risk = []

        priority_data = {
            1: {"total": 0, "breached": 0, "met": 0, "resolution_time": 0.0, "resolved_count": 0},
            2: {"total": 0, "breached": 0, "met": 0, "resolution_time": 0.0, "resolved_count": 0},
            3: {"total": 0, "breached": 0, "met": 0, "resolution_time": 0.0, "resolved_count": 0},
            4: {"total": 0, "breached": 0, "met": 0, "resolution_time": 0.0, "resolved_count": 0},
        }

        for inc in incidents:
            priority = inc.priority or 3
            if priority not in priority_data:
                priority = 3

            priority_data[priority]["total"] += 1

            if inc.sla_deadline:
                if now > inc.sla_deadline and inc.status not in ("resolved", "closed"):
                    breached += 1
                    priority_data[priority]["breached"] += 1
                elif inc.status in ("resolved", "closed"):
                    met += 1
                    priority_data[priority]["met"] += 1

            if inc.resolved_at and inc.created_at:
                resolution_minutes = (inc.resolved_at - inc.created_at).total_seconds() / 60
                total_resolution_time += resolution_minutes
                resolved_count += 1
                priority_data[priority]["resolution_time"] += resolution_minutes
                priority_data[priority]["resolved_count"] += 1

            if inc.sla_deadline and inc.status not in ("resolved", "closed"):
                time_until_deadline = (inc.sla_deadline - now).total_seconds() / 3600
                if 0 < time_until_deadline <= 2:
                    at_risk.append({
                        "incident_id": str(inc.id),
                        "ticket_number": inc.ticket_number,
                        "title": inc.title,
                        "priority": priority,
                        "hours_remaining": round(time_until_deadline, 1),
                    })

        overall_compliance = (met / total * 100) if total > 0 else 0.0
        avg_resolution = total_resolution_time / resolved_count if resolved_count > 0 else 0.0

        by_priority = []
        for p, data in priority_data.items():
            p_level = PriorityLevel.from_int(p)
            compliance = (data["met"] / data["total"] * 100) if data["total"] > 0 else 0.0
            avg_res = data["resolution_time"] / data["resolved_count"] if data["resolved_count"] > 0 else 0.0

            by_priority.append(SLAByPriority(
                priority=p,
                priority_label=p_level.label,
                total_incidents=data["total"],
                breached=data["breached"],
                met=data["met"],
                compliance_rate=compliance,
                avg_response_time_minutes=0.0,
                avg_resolution_time_minutes=avg_res,
            ))

        at_risk.sort(key=lambda x: x["hours_remaining"])

        processing_time = (time.time() - start_time) * 1000

        logger.info(
            "SLA metrics calculated",
            total=total,
            breached=breached,
            compliance=overall_compliance,
        )

        return SLAMetricsResponse(
            overall_compliance_rate=overall_compliance,
            total_incidents=total,
            breached_count=breached,
            met_count=met,
            avg_resolution_time_minutes=avg_resolution,
            by_priority=by_priority,
            at_risk_incidents=at_risk,
            processing_time_ms=processing_time,
        )
