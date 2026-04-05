"""Modelo SQLAlchemy para métricas."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, JSON, String
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..session import Base


class MetricModel(Base):
    """Modelo de base de datos para métricas."""

    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(20), default="gauge")
    category: Mapped[str] = mapped_column(String(50), default="technical")
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    service: Mapped[str] = mapped_column(String(50), default="app")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Metric(id={self.id}, name={self.name}, value={self.value})>"
