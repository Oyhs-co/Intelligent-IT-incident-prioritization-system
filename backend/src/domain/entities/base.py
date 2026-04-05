"""Clase base con getters y setters tipados."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


class BaseEntity(ABC):
    """Clase base abstracta para todas las entidades del dominio."""

    def __init__(self) -> None:
        self._id: UUID = field(default_factory=uuid4)
        self._created_at: datetime = field(default_factory=datetime.utcnow)
        self._updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def id(self) -> UUID:
        """Obtiene el ID único de la entidad."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Obtiene la fecha de creación."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Obtiene la fecha de última modificación."""
        return self._updated_at

    def _mark_updated(self) -> None:
        """Marca la entidad como actualizada."""
        object.__setattr__(self, "_updated_at", datetime.utcnow())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def to_dict(self) -> dict[str, Any]:
        """Convierte la entidad a diccionario."""
        return {
            "id": str(self._id),
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }
