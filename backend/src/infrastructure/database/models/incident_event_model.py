"""Modelo SQLAlchemy para eventos de incidentes."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..session import Base

if TYPE_CHECKING:
    from .incident_model import IncidentModel
    from .user_model import UserModel

class IncidentEventModel(Base):
    """Modelo de base de datos para eventos de auditoría."""

    __tablename__ = "incident_events"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    incident_id: Mapped[str] = mapped_column(
        UUID, ForeignKey("incidents.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[str | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True  # fix: ondelete explícito
    )
    custom_metadata: Mapped[dict] = mapped_column(JSON, default=lambda: {})  # fix: lambda mutable
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False  # fix: server_default
    )
    # fix: updated_at eliminado — log de auditoría es inmutable, solo se crea

    incident: Mapped[IncidentModel] = relationship(
        "IncidentModel",
        back_populates="events",
    )
    user: Mapped[UserModel | None] = relationship("UserModel")

    def __repr__(self) -> str:
        return f"<IncidentEvent(id={self.id}, incident_id={self.incident_id}, type={self.event_type})>"
