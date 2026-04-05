"""Schemas Pydantic para métricas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OverviewMetricsResponse(BaseModel):
    """Métricas generales."""

    total_incidents_today: int
    total_incidents_week: int
    total_incidents_month: int
    incidents_open: int
    incidents_in_progress: int
    incidents_resolved: int
    incidents_closed: int
    avg_response_time_minutes: float
    avg_resolution_time_minutes: float
    sla_compliance_rate: float
    sla_breach_count: int
    model_accuracy: float
    model_confidence_avg: float
    ai_predictions_today: int
    active_users: int
    active_technicians: int


class IncidentMetricsResponse(BaseModel):
    """Métricas de incidentes."""

    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_category: dict[str, int]
    avg_age_by_priority: dict[str, float]
    resolution_rate_by_priority: dict[str, float]


class AIMetricsResponse(BaseModel):
    """Métricas de IA."""

    total_predictions: int
    accuracy: float
    avg_confidence: float
    confidence_distribution: dict[str, int]


class HealthResponse(BaseModel):
    """Response de health check."""

    status: str
    version: str
    timestamp: datetime
    database: str
    ai_model: str
