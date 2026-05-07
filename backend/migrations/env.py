"""Configuración del entorno de migraciones Alembic.

Importa todos los modelos SQLAlchemy para que `Base.metadata` tenga
conocimiento de todas las tablas al generar migraciones automáticas.
Usa `get_sync_engine()` para obtener el motor de base de datos sincrónico
compatible con el driver configurado (SQLite en desarrollo, PostgreSQL en producción).
"""

from logging.config import fileConfig

from sqlalchemy import pool

from alembic import context

from src.infrastructure.database import Base, get_sync_engine
from src.infrastructure.database.models import (
    UserModel,
    IncidentModel,
    CommentModel,
    IncidentEventModel,
    MetricModel,
    IncidentSimilarityModel,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline (sin conexión a BD)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo online (conectado a BD)."""
    connectable = get_sync_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
