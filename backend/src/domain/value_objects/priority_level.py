"""Value Objects para el dominio.

Incluye las entidades de prioridad, estado, categoría, fuente y eventos,
además de las funciones de mapeo entre prioridades de IA y del backend.
"""

from __future__ import annotations

from enum import Enum


class PriorityLevel(Enum):
    """Niveles de prioridad para incidentes."""

    P1_LOW = 1
    P2_MEDIUM = 2
    P3_HIGH = 3
    P4_CRITICAL = 4

    @property
    def label(self) -> str:
        """Etiqueta legible del nivel."""
        labels = {
            1: "Baja",
            2: "Media",
            3: "Alta",
            4: "Crítica",
        }
        return labels[self.value]

    @property
    def sla_minutes(self) -> int:
        """Tiempo SLA en minutos."""
        sla_times = {
            1: 480,  # 8 horas
            2: 240,  # 4 horas
            3: 60,  # 1 hora
            4: 15,  # 15 minutos
        }
        return sla_times[self.value]

    @property
    def color(self) -> str:
        """Color associated with priority."""
        colors = {
            1: "#22C55E",  # Verde
            2: "#EAB308",  # Amarillo
            3: "#F97316",  # Naranja
            4: "#DC2626",  # Rojo
        }
        return colors[self.value]

    @classmethod
    def from_int(cls, value: int) -> PriorityLevel:
        """Crea un PriorityLevel desde un entero."""
        if value not in [1, 2, 3, 4]:
            raise ValueError(f"Valor inválido: {value}")
        return cls(value)

    @classmethod
    def from_string(cls, value: str) -> PriorityLevel:
        """Crea un PriorityLevel desde string."""
        mapping = {
            "P1": 1,
            "LOW": 1,
            "BAJA": 1,
            "1": 1,
            "P2": 2,
            "MEDIUM": 2,
            "MEDIA": 2,
            "2": 2,
            "P3": 3,
            "HIGH": 3,
            "ALTA": 3,
            "3": 3,
            "P4": 4,
            "CRITICAL": 4,
            "CRITICA": 4,
            "4": 4,
        }
        upper = value.upper().strip()
        if upper not in mapping:
            raise ValueError(f"Prioridad inválida: {value}")
        return cls(mapping[upper])


class IncidentStatus(Enum):
    """Estados de un incidente."""

    NEW = "new"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"

    @property
    def is_active(self) -> bool:
        """Verifica si el estado es activo (no cerrado)."""
        return self not in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED, IncidentStatus.REJECTED)

    @property
    def is_final(self) -> bool:
        """Verifica si es estado final."""
        return self in (IncidentStatus.CLOSED, IncidentStatus.REJECTED)

    @classmethod
    def from_string(cls, value: str) -> IncidentStatus:
        """Crea un IncidentStatus desde string."""
        try:
            return cls(value.lower().replace("_", "_"))
        except ValueError:
            raise ValueError(f"Estado inválido: {value}")


class IncidentCategory(Enum):
    """Categorías de incidentes."""

    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    NETWORK = "network"
    SECURITY = "security"
    DATABASE = "database"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    ACCESS = "access"
    OTHER = "other"

    @classmethod
    def from_string(cls, value: str) -> IncidentCategory:
        """Crea una IncidentCategory desde string."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.OTHER


class IncidentSource(Enum):
    """Fuentes de creación de incidentes."""

    WEB = "web"
    API = "api"
    EMAIL = "email"
    INTEGRATION = "integration"
    MANUAL = "manual"


class EventType(Enum):
    """Tipos de eventos de auditoría."""

    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    ASSIGNED = "assigned"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    COMMENT_ADDED = "comment_added"
    DELETED = "deleted"


def map_ia_to_backend(ia_priority: int) -> PriorityLevel:
    """Convierte una prioridad de IA (0-2) a PriorityLevel del backend.

    La IA predice 3 niveles:
        - 0 (P1 Crítico)  → P4_CRITICAL (SLA 15 min)
        - 1 (P2 Medio)    → P2_MEDIUM   (SLA 4 h)
        - 2 (P3 Bajo)     → P1_LOW      (SLA 8 h)

    Args:
        ia_priority: Prioridad devuelta por la IA (0, 1, o 2).

    Returns:
        PriorityLevel correspondiente en el backend.

    Raises:
        ValueError: Si ia_priority no está en [0, 1, 2].
    """
    mapping = {
        0: 4,  # P4_CRITICAL
        1: 2,  # P2_MEDIUM
        2: 1,  # P1_LOW
    }
    if ia_priority not in mapping:
        raise ValueError(
            f"Prioridad de IA inválida: {ia_priority}. Debe ser 0, 1 o 2."
        )
    return PriorityLevel(mapping[ia_priority])


def map_backend_to_ia(backend_priority: PriorityLevel) -> int:
    """Convierte un PriorityLevel del backend a prioridad de IA (0-2).

    Args:
        backend_priority: Prioridad del backend (1-4).

    Returns:
        Prioridad de IA: 0 (crítico), 1 (medio) o 2 (bajo).
    """
    mapping = {
        1: 2,  # P1_LOW → IA 2 (bajo)
        2: 1,  # P2_MEDIUM → IA 1 (medio)
        3: 0,  # P3_HIGH → IA 0 (crítico)
        4: 0,  # P4_CRITICAL → IA 0 (crítico)
    }
    return mapping[backend_priority.value]
