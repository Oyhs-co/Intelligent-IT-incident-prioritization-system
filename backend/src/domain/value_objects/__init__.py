"""Value objects del dominio.

Incluye enumeraciones de prioridad, estado, categoría, fuente y eventos,
además de las funciones de mapeo entre prioridades de IA y del backend.
"""

from .priority_level import (
    EventType,
    IncidentCategory,
    IncidentSource,
    IncidentStatus,
    PriorityLevel,
    map_backend_to_ia,
    map_ia_to_backend,
)

__all__ = [
    "IncidentCategory",
    "IncidentSource",
    "IncidentStatus",
    "PriorityLevel",
    "EventType",
    "map_ia_to_backend",
    "map_backend_to_ia",
]
