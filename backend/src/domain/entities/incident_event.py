"""Entidad IncidentEvent para auditoría."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID

from .base import BaseEntity
from ..value_objects.priority_level import EventType


@dataclass
class IncidentEvent(BaseEntity):
    """Entidad para registrar eventos de auditoría de incidentes."""

    _incident_id: UUID = field(default=None)
    _event_type: EventType = field(default=EventType.CREATED)
    _old_value: Optional[str] = field(default=None)
    _new_value: Optional[str] = field(default=None)
    _user_id: Optional[UUID] = field(default=None)
    _metadata: dict = field(default_factory=dict)

    @property
    def incident_id(self) -> UUID:
        """Obtiene el ID del incidente."""
        return self._incident_id

    @incident_id.setter
    def incident_id(self, value: UUID) -> None:
        """Establece el ID del incidente."""
        object.__setattr__(self, "_incident_id", value)
        self._mark_updated()

    @property
    def event_type(self) -> EventType:
        """Obtiene el tipo de evento."""
        return self._event_type

    @event_type.setter
    def event_type(self, value: EventType) -> None:
        """Establece el tipo de evento."""
        object.__setattr__(self, "_event_type", value)
        self._mark_updated()

    @property
    def old_value(self) -> Optional[str]:
        """Obtiene el valor anterior."""
        return self._old_value

    @property
    def new_value(self) -> Optional[str]:
        """Obtiene el nuevo valor."""
        return self._new_value

    @property
    def user_id(self) -> Optional[UUID]:
        """Obtiene el ID del usuario que realizó el cambio."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: Optional[UUID]) -> None:
        """Establece el ID del usuario."""
        object.__setattr__(self, "_user_id", value)
        self._mark_updated()

    @property
    def metadata(self) -> dict:
        """Obtiene los metadatos del evento."""
        return self._metadata.copy()

    def to_dict(self) -> dict[str, Any]:
        """Convierte la entidad a diccionario."""
        return {
            **super().to_dict(),
            "incident_id": str(self._incident_id),
            "event_type": self._event_type.value,
            "old_value": self._old_value,
            "new_value": self._new_value,
            "user_id": str(self._user_id) if self._user_id else None,
            "metadata": self._metadata,
        }
