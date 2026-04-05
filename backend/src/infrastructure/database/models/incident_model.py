"""Modelo SQLAlchemy para incidentes."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..session import Base


class IncidentModel(Base):
    """Modelo de base de datos para incidentes."""

    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="new", index=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    urgency: Mapped[int] = mapped_column(Integer, default=3)
    impact: Mapped[int] = mapped_column(Integer, default=3)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    sla_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="web")
    tags: Mapped[dict] = mapped_column(JSON, default=list)
    custom_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    reporter_id: Mapped[str | None] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=True
    )
    assigned_to: Mapped[str | None] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=True
    )
    resolved_by: Mapped[str | None] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=True
    )
    closed_by: Mapped[str | None] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=True
    )
    similar_incidents: Mapped[dict] = mapped_column(JSON, default=list)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    reporter: Mapped["UserModel | None"] = relationship(
        "UserModel",
        foreign_keys=[reporter_id],
        back_populates="reported_incidents",
    )
    assignee: Mapped["UserModel | None"] = relationship(
        "UserModel",
        foreign_keys=[assigned_to],
        back_populates="assigned_incidents",
    )
    resolved_by_user: Mapped["UserModel | None"] = relationship(
        "UserModel",
        foreign_keys=[resolved_by],
    )
    closed_by_user: Mapped["UserModel | None"] = relationship(
        "UserModel",
        foreign_keys=[closed_by],
    )
    comments: Mapped[list["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="incident",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["IncidentEventModel"]] = relationship(
        "IncidentEventModel",
        back_populates="incident",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_incidents_created_at", "created_at"),
        Index("ix_incidents_priority_status", "priority", "status"),
    )

    def __repr__(self) -> str:
        return f"<Incident(id={self.id}, ticket={self.ticket_number}, priority={self.priority})>"
