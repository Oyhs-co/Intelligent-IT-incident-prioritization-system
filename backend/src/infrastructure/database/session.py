"""Configuración de base de datos SQLAlchemy.

Soporta dos modos:
  - Desarrollo: SQLite (por defecto, sin servidor externo)
  - Producción: PostgreSQL (requiere servidor postgres en ejecución)

El modo se selecciona automáticamente según DATABASE_URL.
Si la URL contiene "postgresql" → modo producción.
Si la URL contiene "sqlite" → modo desarrollo.
"""

from __future__ import annotations

from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.shared.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos SQLAlchemy."""


_async_engine = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
_sync_engine = None


def get_async_engine():
    """Obtiene el motor async de base de datos (compartido)."""
    global _async_engine
    if _async_engine is None:
        engine_kwargs = dict(
            echo=settings.debug,
            pool_pre_ping=True,
        )

        if settings.is_development:
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        else:
            engine_kwargs["pool_size"] = 10
            engine_kwargs["max_overflow"] = 20

        _async_engine = create_async_engine(
            settings.database_url, **engine_kwargs,
        )
    return _async_engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Obtiene el factory de sesiones async."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_factory


def get_sync_engine():
    """Obtiene el motor sync de base de datos (para migraciones Alembic).

    En desarrollo usa SQLite sync.
    En producción usa el mismo driver sync de PostgreSQL.
    """
    global _sync_engine
    if _sync_engine is None:
        sync_url = settings.database_url_sync
        _sync_engine = create_engine(
            sync_url,
            echo=settings.debug,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False} if "sqlite" in sync_url else {},
        )
    return _sync_engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Generador de sesiones de base de datos.

    Los routes/use cases son responsables del commit/rollback explícito.
    Esta función solo abre la sesión y la cierra al finalizar.
    """
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Inicializa la base de datos creando todas las tablas.

    Ejecuta Base.metadata.create_all para crear las tablas
    si aún no existen (idempotente).
    """
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Cierra las conexiones de base de datos liberando recursos."""
    global _async_engine, _async_session_factory, _sync_engine
    if _async_engine is not None:
        await _async_engine.dispose()
        _async_engine = None
        _async_session_factory = None
    if _sync_engine is not None:
        _sync_engine.dispose()
        _sync_engine = None
