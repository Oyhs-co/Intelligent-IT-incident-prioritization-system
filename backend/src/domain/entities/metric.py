"""Entidades para el sistema de métricas."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class MetricType(Enum):
    """Tipos de métricas."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricCategory(Enum):
    """Categorías de métricas."""

    BUSINESS = "business"
    TECHNICAL = "technical"
    AI_ML = "ai_ml"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class Metric:
    """Representa una métrica individual."""

    _id: UUID = field(default_factory=uuid4)
    _name: str = ""
    _value: float = 0.0
    _metric_type: MetricType = MetricType.GAUGE
    _category: MetricCategory = MetricCategory.TECHNICAL
    _labels: dict = field(default_factory=dict)
    _timestamp: datetime = field(default_factory=datetime.utcnow)
    _service: str = ""

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        object.__setattr__(self, "_name", value)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        object.__setattr__(self, "_value", value)

    @property
    def metric_type(self) -> MetricType:
        return self._metric_type

    @property
    def category(self) -> MetricCategory:
        return self._category

    @property
    def labels(self) -> dict:
        return self._labels.copy()

    @labels.setter
    def labels(self, value: dict) -> None:
        object.__setattr__(self, "_labels", value)

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def service(self) -> str:
        return self._service

    @service.setter
    def service(self, value: str) -> None:
        object.__setattr__(self, "_service", value)

    def to_dict(self) -> dict[str, Any]:
        """Convierte la métrica a diccionario."""
        return {
            "id": str(self._id),
            "name": self._name,
            "value": self._value,
            "type": self._metric_type.value,
            "category": self._category.value,
            "labels": self._labels,
            "timestamp": self._timestamp.isoformat(),
            "service": self._service,
        }


@dataclass
class ServiceMetric:
    """Agrega métricas de un servicio específico."""

    _service_name: str = ""
    _metrics: dict = field(default_factory=dict)
    _health_status: str = "healthy"
    _last_heartbeat: datetime = field(default_factory=datetime.utcnow)

    @property
    def service_name(self) -> str:
        return self._service_name

    @service_name.setter
    def service_name(self, value: str) -> None:
        object.__setattr__(self, "_service_name", value)

    @property
    def metrics(self) -> dict:
        return self._metrics.copy()

    @property
    def health_status(self) -> str:
        return self._health_status

    @health_status.setter
    def health_status(self, value: str) -> None:
        object.__setattr__(self, "_health_status", value)

    @property
    def last_heartbeat(self) -> datetime:
        return self._last_heartbeat

    def update_metric(self, name: str, value: float, metric_type: MetricType) -> None:
        """Actualiza una métrica del servicio."""
        self._metrics[name] = {
            "value": value,
            "type": metric_type.value,
            "updated_at": datetime.utcnow().isoformat(),
        }
        object.__setattr__(self, "_last_heartbeat", datetime.utcnow())

    def record_heartbeat(self) -> None:
        """Registra un latido del servicio."""
        object.__setattr__(self, "_last_heartbeat", datetime.utcnow())

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "service_name": self._service_name,
            "metrics": self._metrics,
            "health_status": self._health_status,
            "last_heartbeat": self._last_heartbeat.isoformat(),
        }
