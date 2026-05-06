"""Modelo SQLAlchemy para similitud entre incidentes."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..session import Base


class IncidentSimilarityModel(Base):
    """Tabla de asociación para incidentes similares.

    Reemplaza el campo JSON similar_incidents en IncidentModel,
    garantizando integridad referencial y consultas eficientes.
    """

    __tablename__ = "incident_similarities"

    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    similar_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<IncidentSimilarity("
            f"incident={self.incident_id}, "
            f"similar={self.similar_id}, "
            f"score={self.score})>"
        )
