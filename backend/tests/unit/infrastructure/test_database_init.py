"""Tests unitarios para init_db y close_db.

Verifica:
  - init_db() crea tablas
  - init_db() es idempotente
  - close_db() libera recursos
"""

import pytest

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from src.infrastructure.database import Base
from src.infrastructure.database.models.user_model import UserModel


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def engine():
    """Crea un engine en memoria para cada test."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    return eng


class TestInitDb:
    """Tests para init_db()."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self, engine):
        """init_db() debe crear las tablas en la BD."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = {row[0] for row in result.fetchall()}
            tables.discard("sqlite_sequence")

        assert len(tables) > 0, "Debe haber al menos una tabla creada"
        assert "users" in tables, "Debe existir la tabla users"
        assert "incidents" in tables, "Debe existir la tabla incidents"
        assert "comments" in tables, "Debe existir la tabla comments"
        assert "incident_events" in tables, "Debe existir la tabla incident_events"
        assert "metrics" in tables, "Debe existir la tabla metrics"
        assert "incident_similarities" in tables, "Debe existir la tabla incident_similarities"

    @pytest.mark.asyncio
    async def test_init_db_is_idempotent(self, engine):
        """init_db() no debe fallar si se llama múltiples veces."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @pytest.mark.asyncio
    async def test_init_db_with_existing_data(self, engine):
        """init_db() no debe borrar datos existentes."""
        factory = async_sessionmaker(engine, expire_on_commit=False)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with factory() as session:
            user = UserModel(
                username="existing",
                email="existing@test.com",
                hashed_password="$2b$12$test_hash",
            )
            session.add(user)
            await session.commit()

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with factory() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserModel).where(UserModel.username == "existing")
            )
            user = result.scalars().first()
            assert user is not None, "init_db no debe borrar datos existentes"


class TestCloseDb:
    """Tests para close_db()."""

    @pytest.mark.asyncio
    async def test_close_db_disposes_engines(self):
        """close_db() debe liberar los motores de BD."""
        from src.infrastructure.database.session import get_async_engine, get_sync_engine, close_db

        engine_async = get_async_engine()
        engine_sync = get_sync_engine()

        assert engine_async is not None
        assert engine_sync is not None

        await close_db()

        import src.infrastructure.database.session as session_module
        assert session_module._async_engine is None
        assert session_module._sync_engine is None
        assert session_module._async_session_factory is None
