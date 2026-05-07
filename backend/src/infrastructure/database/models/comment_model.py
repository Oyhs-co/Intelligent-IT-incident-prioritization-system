"""Modelo SQLAlchemy para comentarios."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from datetime import datetime
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..session import Base


class CommentModel(Base):
    """Modelo de base de datos para comentarios."""

    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    incident_id: Mapped[str] = mapped_column(
        UUID, ForeignKey("incidents.id"), nullable=False, index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True  # fix: ondelete explícito
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    incident: Mapped["IncidentModel"] = relationship(
        "IncidentModel",
        back_populates="comments",
    )
    user: Mapped["UserModel | None"] = relationship("UserModel")

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, incident_id={self.incident_id})>"
