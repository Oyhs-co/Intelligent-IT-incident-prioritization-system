"""Schemas Pydantic para incidentes."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateIncidentRequest(BaseModel):
    """Request para crear un incidente."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    urgency: int = Field(default=3, ge=1, le=5)
    impact: int = Field(default=3, ge=1, le=5)


class UpdateIncidentRequest(BaseModel):
    """Request para actualizar un incidente."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    category: Optional[str] = None


class IncidentResponse(BaseModel):
    """Response de incidente."""

    model_config = {"from_attributes": True}

    id: UUID
    ticket_number: str
    title: str
    description: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    status: str
    priority: Optional[int] = None
    priority_label: Optional[str] = None
    urgency: int
    impact: int
    confidence_score: Optional[float] = None
    explanation: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    source: str
    tags: list[str] = []
    reporter_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    is_sla_breached: bool = False


class IncidentListResponse(BaseModel):
    """Response de lista de incidentes."""

    items: list[IncidentResponse]
    total: int
    skip: int
    limit: int


class ClassificationResponse(BaseModel):
    """Response de clasificación."""

    incident_id: UUID
    priority: int
    priority_label: str
    confidence: float
    explanation: str
    top_features: list[str]
    processing_time_ms: float
