"""Modelo SQLAlchemy para incidentes."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..session import Base

if TYPE_CHECKING:
    from .comment_model import CommentModel
    from .incident_event_model import IncidentEventModel
    from .user_model import UserModel

class IncidentModel(Base):
    """Modelo de base de datos para incidentes."""

    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    ticket_seq: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, default=0)
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="new", index=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    suggested_priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    urgency: Mapped[int] = mapped_column(Integer, default=3)
    impact: Mapped[int] = mapped_column(Integer, default=3)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    sla_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="web")
    tags: Mapped[list] = mapped_column(JSON, default=lambda: [])          # fix: lambda mutable
    custom_metadata: Mapped[dict] = mapped_column(JSON, default=lambda: {})  # fix: lambda mutable
    reporter_id: Mapped[str | None] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    closed_by: Mapped[str | None] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    # fix: similar_incidents eliminado — migrado a tabla incident_similarities
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # fix: server_default
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())  # fix: server_default

    reporter: Mapped[UserModel | None] = relationship(
        "UserModel", foreign_keys=[reporter_id], back_populates="reported_incidents",
    )
    assignee: Mapped[UserModel | None] = relationship(
        "UserModel", foreign_keys=[assigned_to], back_populates="assigned_incidents",
    )
    resolved_by_user: Mapped[UserModel | None] = relationship(
        "UserModel", foreign_keys=[resolved_by],
    )
    closed_by_user: Mapped[UserModel | None] = relationship(
        "UserModel", foreign_keys=[closed_by],
    )
    comments: Mapped[list[CommentModel]] = relationship(
        "CommentModel", back_populates="incident", cascade="all, delete-orphan",
    )
    events: Mapped[list[IncidentEventModel]] = relationship(
        "IncidentEventModel", back_populates="incident", cascade="all, delete-orphan",
    )
    similar_incidents: Mapped[list[IncidentModel]] = relationship(
        "IncidentModel",
        secondary="incident_similarities",
        primaryjoin="IncidentModel.id == foreign(IncidentSimilarityModel.incident_id)",
        secondaryjoin="IncidentModel.id == foreign(IncidentSimilarityModel.similar_id)",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_incidents_created_at", "created_at"),
        Index("ix_incidents_priority_status", "priority", "status"),
        CheckConstraint("priority BETWEEN 1 AND 4", name="ck_priority_range"),      # fix: rango en BD
        CheckConstraint("urgency BETWEEN 1 AND 5", name="ck_urgency_range"),        # fix: rango en BD
        CheckConstraint("impact BETWEEN 1 AND 5", name="ck_impact_range"),          # fix: rango en BD
    )

    def __repr__(self) -> str:
        return f"<Incident(id={self.id}, ticket={self.ticket_number}, priority={self.priority})>"
