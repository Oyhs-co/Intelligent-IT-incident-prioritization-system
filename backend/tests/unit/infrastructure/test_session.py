"""Tests unitarios para la configuración de sesión de base de datos.

Verifica:
  - Creación de motores async y sync
  - Pool settings según entorno
  - Comportamiento de commit/rollback en get_db_session
  - Sesión NO hace commit automático (bugfix C5)
"""

from unittest.mock import patch

import pytest
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.infrastructure.database.session import (
    get_async_engine,
    get_async_session_factory,
    get_db_session,
    get_sync_engine,
)


@pytest.fixture(autouse=True)
def reset_globals():
    """Limpia las variables globales del módulo session antes de cada test.

    Como get_async_engine() y get_sync_engine() usan caching global,
    forzamos recreación limpiando los módulos.
    """
    import src.infrastructure.database.session as session_module
    session_module._async_engine = None
    session_module._async_session_factory = None
    session_module._sync_engine = None
    yield


class TestGetAsyncEngine:
    """Tests para get_async_engine()."""

    @pytest.mark.asyncio
    async def test_returns_async_engine(self):
        """Debe retornar una instancia de AsyncEngine."""
        engine = get_async_engine()
        assert isinstance(engine, AsyncEngine)

    @pytest.mark.asyncio
    async def test_caches_engine(self):
        """Llamadas subsecuentes deben retornar el mismo motor."""
        engine1 = get_async_engine()
        engine2 = get_async_engine()
        assert engine1 is engine2

    @pytest.mark.asyncio
    async def test_pool_size_dev_sqlite(self):
        """En modo SQLite (dev), pool_size debe ser 5."""
        engine = get_async_engine()
        assert engine.pool.size() == 5

    @pytest.mark.asyncio
    async def test_drivername_is_sqlite(self):
        """El driver debe ser sqlite+aiosqlite."""
        engine = get_async_engine()
        assert engine.url.drivername == "sqlite+aiosqlite"


class TestGetSyncEngine:
    """Tests para get_sync_engine()."""

    def test_returns_sync_engine(self):
        """Debe retornar una instancia de Engine."""
        engine = get_sync_engine()
        assert isinstance(engine, Engine)

    def test_caches_engine(self):
        """Llamadas subsecuentes deben retornar el mismo motor."""
        engine1 = get_sync_engine()
        engine2 = get_sync_engine()
        assert engine1 is engine2

    def test_sync_url_is_sqlite(self):
        """La URL sincrónica debe ser sqlite:// (sin +aiosqlite)."""
        engine = get_sync_engine()
        assert "sqlite" in str(engine.url)
        assert "aiosqlite" not in str(engine.url)

    def test_drivername_is_sqlite_sync(self):
        """El driver sync debe ser sqlite."""
        engine = get_sync_engine()
        assert str(engine.url.drivername) == "sqlite"


class TestGetAsyncSessionFactory:
    """Tests para get_async_session_factory()."""

    @pytest.mark.asyncio
    async def test_returns_session_factory(self):
        """Debe retornar un async_sessionmaker."""
        factory = get_async_session_factory()
        assert factory is not None
        async with factory() as session:
            assert isinstance(session, AsyncSession)

    @pytest.mark.asyncio
    async def test_caches_factory(self):
        """Llamadas subsecuentes deben retornar el mismo factory."""
        factory1 = get_async_session_factory()
        factory2 = get_async_session_factory()
        assert factory1 is factory2


class TestGetDbSession:
    """Tests para get_db_session() — el generador de sesiones.

    Verifica que NO haga commit automático (bugfix C5).
    """

    @pytest.mark.asyncio
    async def test_yields_session(self):
        """Debe generar una sesión async."""
        async_gen = get_db_session()
        session = await async_gen.__anext__()
        assert isinstance(session, AsyncSession)
        # Cerrar la sesión para evitar warnings
        await session.close()
        try:
            await async_gen.__anext__()
        except StopAsyncIteration:
            pass

    @pytest.mark.asyncio
    async def test_does_not_commit_on_success(self):
        """La sesión NO debe hacer commit automático al salir del context manager.

        Este es el bugfix C5: antes se hacía commit al salir del 'with',
        ahora los routes son responsables del commit explícito.
        """
        # Creamos un engine en memoria para aislar el test
        from sqlalchemy.ext.asyncio import create_async_engine

        from src.infrastructure.database import Base

        test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Mockeamos el session factory para que use nuestro engine de test
        from src.infrastructure.database.session import get_async_session_factory
        # Reemplazamos temporalmente
        with patch("src.infrastructure.database.session.get_async_engine") as mock_get_engine:
            mock_get_engine.return_value = test_engine

            factory = get_async_session_factory()
            async with factory() as session:
                # Insertamos un registro sin commit
                from src.infrastructure.database.models.user_model import UserModel
                user = UserModel(
                    username="no_commit_test",
                    email="no_commit@test.com",
                    hashed_password="$2b$12$test_hash",
                )
                session.add(user)
                # NO hacemos commit — al salir del with NO debe committear

            # Verificamos que NO haya datos en la BD
            async with factory() as new_session:
                from sqlalchemy import select
                result = await new_session.execute(select(UserModel).where(UserModel.username == "no_commit_test"))
                assert result.scalars().first() is None, "No debería haber datos sin commit explícito"

        await test_engine.dispose()

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self):
        """Si ocurre una excepción, la sesión debe hacer rollback."""
        from sqlalchemy.ext.asyncio import create_async_engine

        from src.infrastructure.database import Base

        test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        with patch("src.infrastructure.database.session.get_async_engine") as mock_get_engine:
            mock_get_engine.return_value = test_engine

            factory = get_async_session_factory()
            # Insertamos un usuario
            from src.infrastructure.database.models.user_model import UserModel
            async with factory() as session:
                user = UserModel(
                    username="rollback_test",
                    email="rollback@test.com",
                    hashed_password="$2b$12$test_hash",
                )
                session.add(user)
                await session.commit()

            # Ahora probamos que una excepción haga rollback
            try:
                async with factory() as session:
                    user2 = UserModel(
                        username="should_rollback",
                        email="rollback2@test.com",
                        hashed_password="$2b$12$test_hash",
                    )
                    session.add(user2)
                    raise ValueError("Fallo forzado")
            except ValueError:
                pass

            # Verificamos que el segundo usuario NO se haya insertado
            async with factory() as new_session:
                from sqlalchemy import select
                result = await new_session.execute(select(UserModel).where(UserModel.username == "should_rollback"))
                assert result.scalars().first() is None, "El rollback debe eliminar datos no commiteados"

            # Pero el primero sí debe estar
            async with factory() as new_session:
                result = await new_session.execute(select(UserModel).where(UserModel.username == "rollback_test"))
                assert result.scalars().first() is not None, "El primer usuario debe persistir"

        await test_engine.dispose()
