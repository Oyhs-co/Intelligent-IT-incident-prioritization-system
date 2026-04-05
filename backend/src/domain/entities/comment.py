"""Entidad Comment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID

from .base import BaseEntity


@dataclass
class Comment(BaseEntity):
    """Entidad que representa un comentario en un incidente."""

    _incident_id: UUID = field(default=None)
    _user_id: UUID = field(default=None)
    _content: str = field(default="")
    _is_internal: bool = field(default=False)

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
    def user_id(self) -> UUID:
        """Obtiene el ID del usuario."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: UUID) -> None:
        """Establece el ID del usuario."""
        object.__setattr__(self, "_user_id", value)
        self._mark_updated()

    @property
    def content(self) -> str:
        """Obtiene el contenido del comentario."""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """Establece el contenido del comentario."""
        value = value.strip()
        if not value:
            raise ValueError("Content cannot be empty")
        object.__setattr__(self, "_content", value)
        self._mark_updated()

    @property
    def is_internal(self) -> bool:
        """Verifica si es un comentario interno."""
        return self._is_internal

    @is_internal.setter
    def is_internal(self, value: bool) -> None:
        """Establece si es un comentario interno."""
        object.__setattr__(self, "_is_internal", value)
        self._mark_updated()

    def to_dict(self) -> dict[str, Any]:
        """Convierte la entidad a diccionario."""
        return {
            **super().to_dict(),
            "incident_id": str(self._incident_id),
            "user_id": str(self._user_id),
            "content": self._content,
            "is_internal": self._is_internal,
        }
