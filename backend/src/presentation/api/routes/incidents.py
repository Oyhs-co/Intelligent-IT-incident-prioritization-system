"""Rutas de incidentes."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from src.application.use_cases.incidents import (
    CreateIncidentUseCase,
    GetIncidentUseCase,
    ListIncidentsUseCase,
    ClassifyIncidentUseCase,
)
from src.application.services import AIService
from src.infrastructure.database import get_db_session
from src.infrastructure.database.repositories import IncidentRepository, EventRepository
from src.domain.repositories import IIncidentRepository, IIncidentEventRepository
from src.presentation.schemas import (
    CreateIncidentRequest,
    IncidentResponse,
    IncidentListResponse,
    ClassificationResponse,
)
from .dependencies import get_current_user, get_ai_service

router = APIRouter(prefix="/api/v1/incidents", tags=["Incidents"])


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    request: CreateIncidentRequest,
    session = Depends(get_db_session),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """Crea un nuevo incidente."""
    incident_repo = IncidentRepository(session)
    event_repo = EventRepository(session)
    ai_svc = await get_ai_service()

    use_case = CreateIncidentUseCase(incident_repo, event_repo, ai_svc)

    user_id = UUID(current_user["id"]) if current_user else None

    incident = await use_case.execute(request, user_id)
    await session.commit()

    return IncidentResponse(
        id=incident.id,
        ticket_number=incident.ticket_number,
        title=incident.title,
        description=incident.description,
        category=incident.category.value if incident.category else None,
        subcategory=incident.subcategory,
        status=incident.status.value,
        priority=incident.priority.value if incident.priority else None,
        priority_label=incident.priority_label,
        urgency=incident.urgency,
        impact=incident.impact,
        confidence_score=incident.confidence_score,
        explanation=incident.explanation,
        sla_deadline=incident.sla_deadline,
        source=incident.source.value,
        tags=incident.tags,
        reporter_id=incident.reporter_id,
        assigned_to=incident.assigned_to,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        is_sla_breached=incident.is_sla_breached,
    )


@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    priority: Optional[int] = Query(None, ge=1, le=4),
    category: Optional[str] = None,
    session = Depends(get_db_session),
):
    """Lista incidentes con filtros."""
    incident_repo = IncidentRepository(session)

    use_case = ListIncidentsUseCase(incident_repo)

    result = await use_case.execute(
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        category=category,
    )

    return IncidentListResponse(
        items=[
            IncidentResponse(
                id=inc.id,
                ticket_number=inc.ticket_number,
                title=inc.title,
                description=inc.description,
                category=inc.category.value if inc.category else None,
                subcategory=inc.subcategory,
                status=inc.status.value,
                priority=inc.priority.value if inc.priority else None,
                priority_label=inc.priority_label,
                urgency=inc.urgency,
                impact=inc.impact,
                confidence_score=inc.confidence_score,
                explanation=inc.explanation,
                sla_deadline=inc.sla_deadline,
                source=inc.source.value,
                tags=inc.tags,
                reporter_id=inc.reporter_id,
                assigned_to=inc.assigned_to,
                created_at=inc.created_at,
                updated_at=inc.updated_at,
                is_sla_breached=inc.is_sla_breached,
            )
            for inc in result.items
        ],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    session = Depends(get_db_session),
):
    """Obtiene un incidente por su ID."""
    incident_repo = IncidentRepository(session)

    use_case = GetIncidentUseCase(incident_repo)

    incident = await use_case.execute(incident_id)

    return IncidentResponse(
        id=incident.id,
        ticket_number=incident.ticket_number,
        title=incident.title,
        description=incident.description,
        category=incident.category.value if incident.category else None,
        subcategory=incident.subcategory,
        status=incident.status.value,
        priority=incident.priority.value if incident.priority else None,
        priority_label=incident.priority_label,
        urgency=incident.urgency,
        impact=incident.impact,
        confidence_score=incident.confidence_score,
        explanation=incident.explanation,
        sla_deadline=incident.sla_deadline,
        source=incident.source.value,
        tags=incident.tags,
        reporter_id=incident.reporter_id,
        assigned_to=incident.assigned_to,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        is_sla_breached=incident.is_sla_breached,
    )


@router.post("/{incident_id}/classify", response_model=ClassificationResponse)
async def classify_incident(
    incident_id: UUID,
    force: bool = Query(False),
    session = Depends(get_db_session),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """Clasifica un incidente usando IA."""
    incident_repo = IncidentRepository(session)
    event_repo = EventRepository(session)
    ai_svc = await get_ai_service()

    use_case = ClassifyIncidentUseCase(incident_repo, event_repo, ai_svc)

    user_id = UUID(current_user["id"]) if current_user else None

    result = await use_case.execute(incident_id, user_id, force)
    await session.commit()

    return ClassificationResponse(
        incident_id=result.incident_id,
        priority=result.priority,
        priority_label=result.priority_label,
        confidence=result.confidence,
        explanation=result.explanation,
        top_features=result.top_features,
        processing_time_ms=result.processing_time_ms,
    )
