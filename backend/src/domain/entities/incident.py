"""Entidad Incident con encapsulamiento completo."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from .base import BaseEntity
from ..value_objects.priority_level import (
    IncidentCategory,
    IncidentSource,
    IncidentStatus,
    PriorityLevel,
)


@dataclass
class Incident(BaseEntity):
    """Entidad de dominio que representa un incidente IT."""

    _ticket_number: str = field(default="")
    _title: str = field(default="")
    _description: str = field(default="")
    _category: Optional[IncidentCategory] = field(default=None)
    _subcategory: Optional[str] = field(default=None)
    _status: IncidentStatus = field(default=IncidentStatus.NEW)
    _priority: Optional[PriorityLevel] = field(default=None)
    _urgency: int = field(default=3)
    _impact: int = field(default=3)
    _confidence_score: Optional[float] = field(default=None)
    _explanation: Optional[str] = field(default=None)
    _sla_deadline: Optional[datetime] = field(default=None)
    _resolution: Optional[str] = field(default=None)
    _resolution_code: Optional[str] = field(default=None)
    _source: IncidentSource = field(default=IncidentSource.WEB)
    _tags: list[str] = field(default_factory=list)
    _metadata: dict = field(default_factory=dict)
    _reporter_id: Optional[UUID] = field(default=None)
    _assigned_to: Optional[UUID] = field(default=None)
    _resolved_by: Optional[UUID] = field(default=None)
    _closed_by: Optional[UUID] = field(default=None)
    _similar_incidents: list[UUID] = field(default_factory=list)
    _resolved_at: Optional[datetime] = field(default=None)
    _closed_at: Optional[datetime] = field(default=None)

    @property
    def ticket_number(self) -> str:
        """Obtiene el número de ticket."""
        return self._ticket_number

    @ticket_number.setter
    def ticket_number(self, value: str) -> None:
        """Establece el número de ticket."""
        object.__setattr__(self, "_ticket_number", value.strip().upper())
        self._mark_updated()

    @property
    def title(self) -> str:
        """Obtiene el título del incidente."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Establece el título del incidente."""
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty")
        if len(value) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        object.__setattr__(self, "_title", value)
        self._mark_updated()

    @property
    def description(self) -> str:
        """Obtiene la descripción del incidente."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Establece la descripción del incidente."""
        value = value.strip()
        if not value:
            raise ValueError("Description cannot be empty")
        if len(value) > 5000:
            raise ValueError("Description cannot exceed 5000 characters")
        object.__setattr__(self, "_description", value)
        self._mark_updated()

    @property
    def category(self) -> Optional[IncidentCategory]:
        """Obtiene la categoría del incidente."""
        return self._category

    @category.setter
    def category(self, value: Optional[IncidentCategory]) -> None:
        """Establece la categoría del incidente."""
        object.__setattr__(self, "_category", value)
        self._mark_updated()

    @property
    def subcategory(self) -> Optional[str]:
        """Obtiene la subcategoría del incidente."""
        return self._subcategory

    @subcategory.setter
    def subcategory(self, value: Optional[str]) -> None:
        """Establece la subcategoría del incidente."""
        object.__setattr__(self, "_subcategory", value)
        self._mark_updated()

    @property
    def status(self) -> IncidentStatus:
        """Obtiene el estado actual del incidente."""
        return self._status

    @status.setter
    def status(self, value: IncidentStatus) -> None:
        """Establece el estado del incidente."""
        object.__setattr__(self, "_status", value)
        self._mark_updated()

    @property
    def priority(self) -> Optional[PriorityLevel]:
        """Obtiene la prioridad asignada."""
        return self._priority

    @property
    def priority_label(self) -> Optional[str]:
        """Obtiene la etiqueta de prioridad."""
        return self._priority.label if self._priority else None

    @priority.setter
    def priority(self, value: Optional[PriorityLevel]) -> None:
        """Establece la prioridad del incidente."""
        object.__setattr__(self, "_priority", value)
        self._mark_updated()

    @property
    def urgency(self) -> int:
        """Obtiene el nivel de urgencia (1-5)."""
        return self._urgency

    @urgency.setter
    def urgency(self, value: int) -> None:
        """Establece el nivel de urgencia."""
        if not 1 <= value <= 5:
            raise ValueError("Urgency must be between 1 and 5")
        object.__setattr__(self, "_urgency", value)
        self._mark_updated()

    @property
    def impact(self) -> int:
        """Obtiene el nivel de impacto (1-5)."""
        return self._impact

    @impact.setter
    def impact(self, value: int) -> None:
        """Establece el nivel de impacto."""
        if not 1 <= value <= 5:
            raise ValueError("Impact must be between 1 and 5")
        object.__setattr__(self, "_impact", value)
        self._mark_updated()

    @property
    def confidence_score(self) -> Optional[float]:
        """Obtiene el score de confianza."""
        return self._confidence_score

    @property
    def explanation(self) -> Optional[str]:
        """Obtiene la explicación de priorización."""
        return self._explanation

    @property
    def sla_deadline(self) -> Optional[datetime]:
        """Obtiene la fecha límite de SLA."""
        return self._sla_deadline

    @property
    def reporter_id(self) -> Optional[UUID]:
        """Obtiene el ID del reporter."""
        return self._reporter_id

    @reporter_id.setter
    def reporter_id(self, value: Optional[UUID]) -> None:
        """Establece el ID del reporter."""
        object.__setattr__(self, "_reporter_id", value)
        self._mark_updated()

    @property
    def assigned_to(self) -> Optional[UUID]:
        """Obtiene el ID del técnico asignado."""
        return self._assigned_to

    @property
    def resolved_by(self) -> Optional[UUID]:
        """Obtiene el ID de quien resolvió."""
        return self._resolved_by

    @property
    def closed_by(self) -> Optional[UUID]:
        """Obtiene el ID de quien cerró."""
        return self._closed_by

    @property
    def similar_incidents(self) -> list[UUID]:
        """Obtiene la lista de incidentes similares."""
        return self._similar_incidents.copy()

    @property
    def source(self) -> IncidentSource:
        """Obtiene la fuente del incidente."""
        return self._source

    @property
    def tags(self) -> list[str]:
        """Obtiene las etiquetas."""
        return self._tags.copy()

    @property
    def metadata(self) -> dict:
        """Obtiene los metadatos."""
        return self._metadata.copy()

    @property
    def resolved_at(self) -> Optional[datetime]:
        """Obtiene la fecha de resolución."""
        return self._resolved_at

    @property
    def closed_at(self) -> Optional[datetime]:
        """Obtiene la fecha de cierre."""
        return self._closed_at

    @property
    def age(self) -> timedelta:
        """Obtiene la edad del incidente."""
        return datetime.utcnow() - self._created_at

    @property
    def is_sla_breached(self) -> bool:
        """Verifica si se ha superado el SLA."""
        if self._sla_deadline is None:
            return False
        return datetime.utcnow() > self._sla_deadline

    @property
    def is_sla_at_risk(self) -> bool:
        """Verifica si el SLA está en riesgo (menos de 15 min)."""
        if self._sla_deadline is None:
            return False
        remaining = self._sla_deadline - datetime.utcnow()
        return timedelta(0) < remaining < timedelta(minutes=15)

    def assign_priority(
        self,
        priority: PriorityLevel,
        confidence: float,
        explanation: str,
        similar: Optional[list[UUID]] = None,
    ) -> None:
        """Asigna la priorización al incidente."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        object.__setattr__(self, "_priority", priority)
        object.__setattr__(self, "_confidence_score", confidence)
        object.__setattr__(self, "_explanation", explanation)
        object.__setattr__(self, "_similar_incidents", similar or [])
        object.__setattr__(
            self, "_sla_deadline", datetime.utcnow() + timedelta(minutes=priority.sla_minutes)
        )
        self._mark_updated()

    def escalate(self) -> PriorityLevel:
        """Escala el incidente a la siguiente prioridad."""
        escalation_map = {
            PriorityLevel.P1_LOW: PriorityLevel.P2_MEDIUM,
            PriorityLevel.P2_MEDIUM: PriorityLevel.P3_HIGH,
            PriorityLevel.P3_HIGH: PriorityLevel.P4_CRITICAL,
            PriorityLevel.P4_CRITICAL: PriorityLevel.P4_CRITICAL,
        }

        if self._priority is None:
            new_priority = PriorityLevel.P3_HIGH
        else:
            new_priority = escalation_map[self._priority]

        object.__setattr__(self, "_priority", new_priority)
        if self._sla_deadline:
            object.__setattr__(
                self,
                "_sla_deadline",
                datetime.utcnow() + timedelta(minutes=new_priority.sla_minutes),
            )
        self._mark_updated()

        return new_priority

    def should_escalate(self) -> bool:
        """Determina si el incidente debe escalar."""
        if self._priority is None:
            return True
        return self._priority in (PriorityLevel.P3_HIGH, PriorityLevel.P4_CRITICAL) and self.age > timedelta(
            hours=1
        )

    def assign_to(self, assignee_id: UUID) -> None:
        """Asigna el incidente a un técnico."""
        object.__setattr__(self, "_assigned_to", assignee_id)
        if self._status == IncidentStatus.NEW or self._status == IncidentStatus.OPEN:
            object.__setattr__(self, "_status", IncidentStatus.IN_PROGRESS)
        self._mark_updated()

    def resolve(self, resolution: str, resolved_by: UUID, resolution_code: Optional[str] = None) -> None:
        """Marca el incidente como resuelto."""
        object.__setattr__(self, "_status", IncidentStatus.RESOLVED)
        object.__setattr__(self, "_resolution", resolution)
        object.__setattr__(self, "_resolved_by", resolved_by)
        object.__setattr__(self, "_resolution_code", resolution_code)
        object.__setattr__(self, "_resolved_at", datetime.utcnow())
        self._mark_updated()

    def close(self, closed_by: UUID) -> None:
        """Cierra el incidente."""
        object.__setattr__(self, "_status", IncidentStatus.CLOSED)
        object.__setattr__(self, "_closed_by", closed_by)
        object.__setattr__(self, "_closed_at", datetime.utcnow())
        self._mark_updated()

    def reopen(self, reason: str) -> None:
        """Reabre el incidente."""
        object.__setattr__(self, "_status", IncidentStatus.OPEN)
        self._metadata["reopen_reason"] = reason
        self._mark_updated()

    def add_tag(self, tag: str) -> None:
        """Agrega una etiqueta."""
        if tag not in self._tags:
            self._tags.append(tag)
            self._mark_updated()

    def to_dict(self) -> dict[str, Any]:
        """Convierte la entidad a diccionario."""
        return {
            **super().to_dict(),
            "ticket_number": self._ticket_number,
            "title": self._title,
            "description": self._description,
            "category": self._category.value if self._category else None,
            "subcategory": self._subcategory,
            "status": self._status.value,
            "priority": self._priority.value if self._priority else None,
            "priority_label": self.priority_label,
            "urgency": self._urgency,
            "impact": self._impact,
            "confidence_score": self._confidence_score,
            "explanation": self._explanation,
            "sla_deadline": self._sla_deadline.isoformat() if self._sla_deadline else None,
            "resolution": self._resolution,
            "resolution_code": self._resolution_code,
            "source": self._source.value,
            "tags": self._tags,
            "metadata": self._metadata,
            "reporter_id": str(self._reporter_id) if self._reporter_id else None,
            "assigned_to": str(self._assigned_to) if self._assigned_to else None,
            "resolved_by": str(self._resolved_by) if self._resolved_by else None,
            "closed_by": str(self._closed_by) if self._closed_by else None,
            "similar_incidents": [str(x) for x in self._similar_incidents],
            "resolved_at": self._resolved_at.isoformat() if self._resolved_at else None,
            "closed_at": self._closed_at.isoformat() if self._closed_at else None,
            "age_seconds": self.age.total_seconds(),
            "is_sla_breached": self.is_sla_breached,
        }
