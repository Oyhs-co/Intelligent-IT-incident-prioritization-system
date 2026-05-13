"""Clase base para todas las entidades del dominio.

Proporciona ID único, timestamps de creación/actualización, igualdad
por identidad y conversión a diccionario.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class BaseEntity:
    """Clase base para todas las entidades del dominio."""

    _id: UUID = field(default_factory=uuid4, init=False, repr=False)
    _created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        init=False,
        repr=False,
    )
    _updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        init=False,
        repr=False,
    )

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
        object.__setattr__(self, "_updated_at", datetime.now(UTC))

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
