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
)
from .dependencies import get_ai_service

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@router.get("/overview", response_model=OverviewMetricsResponse)
async def get_overview_metrics():
    """Obtiene métricas generales del sistema."""
    async for session in get_db_session():
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
async def get_incident_metrics():
    """Obtiene métricas detalladas de incidentes."""
    async for session in get_db_session():
        metrics_service = MetricsService(session)

        metrics = await metrics_service.get_incident_metrics()

        return IncidentMetricsResponse(
            by_status=metrics.by_status,
            by_priority=metrics.by_priority,
            by_category=metrics.by_category,
            avg_age_by_priority=metrics.avg_age_by_priority,
            resolution_rate_by_priority=metrics.resolution_rate_by_priority,
        )


@router.get("/ai", response_model=AIMetricsResponse)
async def get_ai_metrics():
    """Obtiene métricas de IA."""
    async for session in get_db_session():
        metrics_service = MetricsService(session)

        metrics = await metrics_service.get_ai_metrics()

        return AIMetricsResponse(
            total_predictions=metrics.total_predictions,
            accuracy=metrics.accuracy,
            avg_confidence=metrics.avg_confidence,
            confidence_distribution=metrics.confidence_distribution,
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
