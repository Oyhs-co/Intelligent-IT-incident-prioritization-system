"""Rutas de métricas."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.application.services import AIService, MetricsService
from src.infrastructure.database import get_db_session
from src.presentation.schemas import (
    OverviewMetricsResponse,
    IncidentMetricsResponse,
    AIMetricsResponse,
    HealthResponse,
    SLAMetricsResponse,
)
from .dependencies import get_ai_service

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@router.get("/overview", response_model=OverviewMetricsResponse)
async def get_overview_metrics(session = Depends(get_db_session)):
    """Obtiene métricas generales del sistema."""
    metrics_service = MetricsService(session)

    metrics = await metrics_service.get_overview_metrics()

    return OverviewMetricsResponse(
        total_incidents_today=metrics.total_incidents_today,
        total_incidents_week=metrics.total_incidents_week,
        total_incidents_month=metrics.total_incidents_month,
        incidents_open=metrics.incidents_open,
        incidents_in_progress=metrics.incidents_in_progress,
        incidents_resolved=metrics.incidents_resolved,
        incidents_closed=metrics.incidents_closed,
        avg_response_time_minutes=metrics.avg_response_time_minutes,
        avg_resolution_time_minutes=metrics.avg_resolution_time_minutes,
        sla_compliance_rate=metrics.sla_compliance_rate,
        sla_breach_count=metrics.sla_breach_count,
        model_accuracy=metrics.model_accuracy,
        model_confidence_avg=metrics.model_confidence_avg,
        ai_predictions_today=metrics.ai_predictions_today,
        active_users=metrics.active_users,
        active_technicians=metrics.active_technicians,
    )


@router.get("/incidents", response_model=IncidentMetricsResponse)
async def get_incident_metrics(session = Depends(get_db_session)):
    """Obtiene métricas detalladas de incidentes."""
    metrics_service = MetricsService(session)

    metrics = await metrics_service.get_incident_metrics()

    return IncidentMetricsResponse(
        by_status=metrics.by_status,
        by_priority={str(k): v for k, v in metrics.by_priority.items()},
        by_category=metrics.by_category,
        avg_age_by_priority={str(k): v for k, v in metrics.avg_age_by_priority.items()},
        resolution_rate_by_priority={str(k): v for k, v in metrics.resolution_rate_by_priority.items()},
    )


@router.get("/ai", response_model=AIMetricsResponse)
async def get_ai_metrics(session = Depends(get_db_session)):
    """Obtiene métricas de IA."""
    metrics_service = MetricsService(session)

    metrics = await metrics_service.get_ai_metrics()

    return AIMetricsResponse(
        total_predictions=metrics.total_predictions,
        accuracy=metrics.accuracy,
        avg_confidence=metrics.avg_confidence,
        confidence_distribution=metrics.confidence_distribution,
    )


@router.get("/sla", response_model=SLAMetricsResponse)
async def get_sla_metrics(session=Depends(get_db_session)):
    """Obtiene métricas de SLA."""
    from src.application.use_cases.metrics import GetSLAMetricsUseCase

    use_case = GetSLAMetricsUseCase(session)

    metrics = await use_case.execute()

    return SLAMetricsResponse(
        overall_compliance_rate=metrics.overall_compliance_rate,
        total_incidents=metrics.total_incidents,
        breached_count=metrics.breached_count,
        met_count=metrics.met_count,
        avg_resolution_time_minutes=metrics.avg_resolution_time_minutes,
        by_priority=[
            {
                "priority": p.priority,
                "priority_label": p.priority_label,
                "total_incidents": p.total_incidents,
                "breached": p.breached,
                "met": p.met,
                "compliance_rate": p.compliance_rate,
                "avg_response_time_minutes": p.avg_response_time_minutes,
                "avg_resolution_time_minutes": p.avg_resolution_time_minutes,
            }
            for p in metrics.by_priority
        ],
        at_risk_incidents=metrics.at_risk_incidents,
        processing_time_ms=metrics.processing_time_ms,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del sistema."""
    ai_svc = await get_ai_service()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        database="connected",
        ai_model="loaded" if ai_svc.is_model_available() else "not_loaded",
    )
