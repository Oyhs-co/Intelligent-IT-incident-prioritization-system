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
    subcategory: Optional[str] = None
    urgency: Optional[int] = Field(None, ge=1, le=5)
    impact: Optional[int] = Field(None, ge=1, le=5)
    resolution: Optional[str] = None
    resolution_code: Optional[str] = None
    tags: Optional[list[str]] = None
    assigned_to: Optional[UUID] = None


class AddCommentRequest(BaseModel):
    """Request para agregar un comentario."""

    content: str = Field(..., min_length=1, max_length=2000)
    is_internal: bool = False


class SearchSimilarRequest(BaseModel):
    """Request para buscar incidentes similares."""

    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=5, ge=1, le=50)
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)


class EventResponse(BaseModel):
    """Response de evento de incidente."""

    model_config = {"from_attributes": True}

    id: UUID
    incident_id: UUID
    event_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    user_id: Optional[UUID] = None
    custom_metadata: dict = {}
    created_at: datetime


class CommentResponse(BaseModel):
    """Response de comentario."""

    model_config = {"from_attributes": True}

    id: UUID
    incident_id: UUID
    user_id: Optional[UUID] = None
    content: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime


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
