"""Rutas de incidentes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.use_cases.ai import (
    GetRecommendationsRequest,
    GetRecommendationsUseCase,
    SearchSimilarIncidentsUseCase,
)
from src.application.use_cases.incidents import (
    ClassifyIncidentUseCase,
    CreateIncidentUseCase,
    DeleteIncidentUseCase,
    GetIncidentUseCase,
    ListIncidentsUseCase,
    UpdateIncidentUseCase,
)
from src.domain.entities.incident_event import IncidentEvent
from src.domain.value_objects import EventType
from src.infrastructure.database import get_db_session
from src.infrastructure.database.repositories import (
    CommentRepository,
    EventRepository,
    IncidentRepository,
    UserRepository,
)
from src.presentation.schemas import (
    AddCommentRequest,
    ClassificationResponse,
    CommentResponse,
    EventResponse,
    IncidentListResponse,
    IncidentResponse,
    SearchSimilarRequest,
    UpdateIncidentRequest,
)
from src.presentation.schemas import (
    CreateIncidentRequest as CreateIncidentSchema,
)

from .dependencies import get_ai_service, get_current_user

router = APIRouter(prefix="/api/v1/incidents", tags=["Incidents"])


@router.get("/categories")
async def list_categories():
    """Lista las categorías/departamentos disponibles."""
    from src.domain.value_objects import IncidentCategory
    return [
        {"value": c.value, "label": _category_label(c)}
        for c in IncidentCategory
    ]


@router.get("/priorities")
async def list_priorities():
    """Lista los niveles de prioridad disponibles."""
    from src.domain.value_objects import PriorityLevel
    return [
        {"value": p.value, "label": p.label}
        for p in PriorityLevel
    ]


def _category_label(cat) -> str:
    labels = {
        "infrastructure": "Infraestructura",
        "application": "Soporte General",
        "network": "Redes",
        "security": "Seguridad",
        "database": "Bases de Datos",
        "hardware": "Soporte de Hardware",
        "software": "Desarrollo de Software",
        "access": "Cuentas y Accesos",
        "other": "Otros",
    }
    return labels.get(cat.value, cat.value)


CATEGORY_TO_DEPARTMENT = {
    "infrastructure": "Infrastructure",
    "application": "Support",
    "network": "Network",
    "security": "Security",
    "database": "Infrastructure",
    "hardware": "Support",
    "software": "Support",
    "access": "Security",
}


def _incident_to_response(inc) -> IncidentResponse:
    return IncidentResponse(
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
        resolution=inc.resolution,
        resolution_code=inc.resolution_code,
        resolved_at=inc.resolved_at,
        created_at=inc.created_at,
        updated_at=inc.updated_at,
        is_sla_breached=inc.is_sla_breached,
    )


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    request: CreateIncidentSchema,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Crea un nuevo incidente."""
    incident_repo = IncidentRepository(session)
    event_repo = EventRepository(session)
    ai_svc = await get_ai_service()

    use_case = CreateIncidentUseCase(incident_repo, event_repo, ai_svc)

    from src.application.use_cases.incidents.create_incident import (
        CreateIncidentRequest as CreateIncidentReq,
    )

    uc_request = CreateIncidentReq(
        title=request.title,
        description=request.description,
        category=request.category,
        subcategory=request.subcategory,
        urgency=request.urgency,
        impact=request.impact,
        source="web",
    )

    user_id = UUID(current_user["id"]) if current_user else None

    incident = await use_case.execute(uc_request, user_id)
    await session.commit()

    return _incident_to_response(incident)


@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = None,
    priority: int | None = Query(None, ge=1, le=4),
    category: str | None = None,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Lista incidentes con filtros y control de roles."""
    incident_repo = IncidentRepository(session)

    use_case = ListIncidentsUseCase(incident_repo)

    assigned_to = None
    created_by = None
    assigned_department = None

    if current_user:
        role = current_user.get("role")
        user_id = UUID(current_user["id"]) if current_user.get("id") else None

        if role == "user":
            created_by = user_id
        elif role == "technician":
            assigned_department = current_user.get("department")

    result = await use_case.execute(
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        category=category,
        assigned_to=assigned_to,
        created_by=created_by,
        assigned_department=assigned_department,
    )

    return IncidentListResponse(
        items=[_incident_to_response(inc) for inc in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    session=Depends(get_db_session),
):
    """Obtiene un incidente por su ID."""
    incident_repo = IncidentRepository(session)

    use_case = GetIncidentUseCase(incident_repo)

    try:
        incident = await use_case.execute(incident_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found",
        ) from e

    return _incident_to_response(incident)


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    request: UpdateIncidentRequest,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Actualiza un incidente parcialmente."""
    incident_repo = IncidentRepository(session)
    event_repo = EventRepository(session)

    use_case = UpdateIncidentUseCase(incident_repo, event_repo)

    user_id = UUID(current_user["id"]) if current_user else None

    try:
        incident = await use_case.execute(
            incident_id=incident_id,
            title=request.title,
            description=request.description,
            category=request.category,
            subcategory=request.subcategory,
            status=request.status,
            priority=request.priority,
            urgency=request.urgency,
            impact=request.impact,
            resolution=request.resolution,
            resolution_code=request.resolution_code,
            tags=request.tags,
            assigned_to=request.assigned_to,
            user_id=user_id,
        )

        if request.category is not None and request.assigned_to is None:
            dept = CATEGORY_TO_DEPARTMENT.get(request.category)
            if dept:
                user_repo = UserRepository(session)
                techs, _ = await user_repo.list_all(
                    role="technician", is_active=True, department=dept, limit=1
                )
                if techs:
                    incident.assign_to(techs[0].id)
                    await incident_repo.update(incident)
                    assign_event = IncidentEvent()
                    assign_event.incident_id = incident.id
                    assign_event.event_type = EventType.ASSIGNED
                    assign_event.user_id = user_id
                    assign_event.metadata = {
                        "assigned_to": str(techs[0].id),
                        "department": dept,
                    }
                    await event_repo.create(assign_event)

        await session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )from e

    return _incident_to_response(incident)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: UUID,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Elimina un incidente."""
    incident_repo = IncidentRepository(session)
    event_repo = EventRepository(session)

    use_case = DeleteIncidentUseCase(incident_repo, event_repo)

    user_id = UUID(current_user["id"]) if current_user else None

    deleted = await use_case.execute(incident_id, user_id)
    await session.commit()

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found",
        )

    return None


@router.post("/{incident_id}/classify", response_model=ClassificationResponse)
async def classify_incident(
    incident_id: UUID,
    force: bool = Query(False),
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
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


@router.post("/{incident_id}/recommendations")
async def get_recommendations(
    incident_id: UUID,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Obtiene recomendaciones basadas en incidentes similares."""
    incident_repo = IncidentRepository(session)

    use_case = GetRecommendationsUseCase(incident_repo)

    request = GetRecommendationsRequest(incident_id=incident_id)

    try:
        result = await use_case.execute(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )from e

    return {
        "incident_id": str(result.incident_id),
        "recommended_priority": result.recommended_priority,
        "recommended_priority_label": result.recommended_priority_label,
        "confidence": result.confidence,
        "similar_incidents_count": result.similar_incidents_count,
        "avg_resolution_time_hours": result.avg_resolution_time_hours,
        "suggested_actions": result.suggested_actions,
        "explanation": result.explanation,
        "processing_time_ms": result.processing_time_ms,
    }


@router.post("/similar")
async def search_similar(
    request: SearchSimilarRequest,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Busca incidentes similares."""
    incident_repo = IncidentRepository(session)

    use_case = SearchSimilarIncidentsUseCase(incident_repo)

    results = await use_case.execute(
        query=request.query,
        limit=request.limit,
        min_similarity=request.min_similarity,
    )

    return {
        "items": [
            {
                "incident_id": str(r.incident_id),
                "ticket_number": r.ticket_number,
                "title": r.title,
                "description": r.description,
                "priority": r.priority,
                "priority_label": r.priority_label,
                "status": r.status,
                "similarity_score": r.similarity_score,
                "category": r.category,
                "resolution_time_hours": r.resolution_time_hours,
                "resolution": r.resolution,
            }
            for r in results
        ],
        "total": len(results),
    }


@router.get("/{incident_id}/events", response_model=list[EventResponse])
async def get_incident_events(
    incident_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Obtiene los eventos de auditoría de un incidente."""
    event_repo = EventRepository(session)

    events, total = await event_repo.list_by_incident(
        incident_id, skip=skip, limit=limit
    )

    return [
        EventResponse(
            id=e.id,
            incident_id=e.incident_id,
            event_type=e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type),
            old_value=e.old_value,
            new_value=e.new_value,
            user_id=e.user_id,
            custom_metadata=e.metadata,
            created_at=e.created_at,
        )
        for e in events
    ]


@router.get("/{incident_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    incident_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_internal: bool = Query(False),
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Lista los comentarios de un incidente."""
    comment_repo = CommentRepository(session)

    comments, total = await comment_repo.list_by_incident(
        incident_id, skip=skip, limit=limit, include_internal=include_internal
    )

    return [
        CommentResponse(
            id=c.id,
            incident_id=c.incident_id,
            user_id=c.user_id,
            content=c.content,
            is_internal=c.is_internal,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in comments
    ]


@router.post(
    "/{incident_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)

async def add_comment(
    incident_id: UUID,
    request: AddCommentRequest,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Agrega un comentario a un incidente."""
    from src.domain.entities.comment import Comment

    comment_repo = CommentRepository(session)

    user_id = UUID(current_user["id"]) if current_user else None

    comment = Comment()
    comment.incident_id = incident_id
    comment.user_id = user_id
    comment.content = request.content
    comment.is_internal = request.is_internal

    saved = await comment_repo.create(comment)
    await session.commit()

    return CommentResponse(
        id=saved.id,
        incident_id=saved.incident_id,
        user_id=saved.user_id,
        content=saved.content,
        is_internal=saved.is_internal,
        created_at=saved.created_at,
        updated_at=saved.updated_at,
    )
