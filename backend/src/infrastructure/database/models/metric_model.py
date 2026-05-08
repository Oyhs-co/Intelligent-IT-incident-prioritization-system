"""Modelo SQLAlchemy para métricas."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (  # fix: Column, UUID sin uso eliminados
    JSON,
    DateTime,
    Float,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..session import Base


class MetricModel(Base):
    """Modelo de base de datos para métricas."""

    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(20), default="gauge")
    category: Mapped[str] = mapped_column(String(50), default="technical")
    labels: Mapped[dict] = mapped_column(JSON, default=lambda: {})  # fix: lambda mutable
    service: Mapped[str] = mapped_column(String(50), default="app")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),  # fix: server_default evaluado por la BD en cada INSERT
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Metric(id={self.id}, name={self.name}, value={self.value})>"
