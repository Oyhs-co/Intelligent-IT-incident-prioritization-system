"""Tests de integración para la conexión de base de datos.

Verifica CRUD básico con sesión async usando el patrón del conftest
(engine en memoria), probando que la configuración SQLAlchemy async
funciona correctamente con commits/rollbacks explícitos.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.database import Base
from src.infrastructure.database.models.comment_model import CommentModel
from src.infrastructure.database.models.incident_model import IncidentModel
from src.infrastructure.database.models.user_model import UserModel

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def engine():
    """Crea engine en memoria y tablas para el módulo de tests."""
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def session(engine) -> AsyncSession:
    """Crea una sesión nueva para cada test."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.fixture
async def clean_session(engine) -> AsyncSession:
    """Crea sesión y limpia todas las tablas al finalizar."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()
        # Limpia datos después de cada test
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


class TestDatabaseCRUD:
    """CRUD básico con sesión async."""

    @pytest.mark.asyncio
    async def test_create_and_read_user(self, clean_session):
        """Crear un usuario y leerlo desde la BD."""
        user = UserModel(
            username="crud_user",
            email="crud@test.com",
            hashed_password="$2b$12$test_hash",
        )
        clean_session.add(user)
        await clean_session.commit()
        user_id = user.id

        result = await clean_session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        loaded = result.scalars().first()
        assert loaded is not None
        assert loaded.username == "crud_user"
        assert loaded.email == "crud@test.com"

    @pytest.mark.asyncio
    async def test_create_and_read_incident(self, clean_session):
        """Crear un incidente con relaciones."""
        user = UserModel(
            username="inc_user",
            email="inc@test.com",
            hashed_password="$2b$12$test_hash",
        )
        clean_session.add(user)
        await clean_session.commit()

        incident = IncidentModel(
            ticket_seq=1,
            ticket_number="INC-TEST-001",
            title="Test Incident CRUD",
            description="Descripción de prueba",
            reporter_id=user.id,
            urgency=3,
            impact=3,
            source="web",
            status="new",
        )
        clean_session.add(incident)
        await clean_session.commit()
        incident_id = incident.id

        result = await clean_session.execute(
            select(IncidentModel).where(IncidentModel.id == incident_id)
        )
        loaded = result.scalars().first()
        assert loaded is not None
        assert loaded.title == "Test Incident CRUD"
        assert loaded.ticket_number == "INC-TEST-001"
        assert loaded.status == "new"

    @pytest.mark.asyncio
    async def test_update_user(self, clean_session):
        """Actualizar un usuario existente."""
        user = UserModel(
            username="update_user",
            email="update@test.com",
            hashed_password="$2b$12$test_hash",
            first_name="Old",
        )
        clean_session.add(user)
        await clean_session.commit()
        user_id = user.id

        loaded = await clean_session.get(UserModel, user_id)
        loaded.first_name = "Updated"
        await clean_session.commit()

        loaded = await clean_session.get(UserModel, user_id)
        assert loaded.first_name == "Updated"

    @pytest.mark.asyncio
    async def test_delete_user(self, clean_session):
        """Eliminar un usuario."""
        user = UserModel(
            username="delete_user",
            email="delete@test.com",
            hashed_password="$2b$12$test_hash",
        )
        clean_session.add(user)
        await clean_session.commit()
        user_id = user.id

        loaded = await clean_session.get(UserModel, user_id)
        await clean_session.delete(loaded)
        await clean_session.commit()

        loaded = await clean_session.get(UserModel, user_id)
        assert loaded is None, "El usuario debe haber sido eliminado"

    @pytest.mark.asyncio
    async def test_relationship_incident_comments(self, clean_session):
        """Verificar relación entre incidente y comentarios."""
        user = UserModel(
            username="rel_user",
            email="rel@test.com",
            hashed_password="$2b$12$test_hash",
        )
        clean_session.add(user)
        await clean_session.commit()

        incident = IncidentModel(
            ticket_seq=1,
            ticket_number="INC-REL-001",
            title="Relational Test",
            description="Testing relationships",
            reporter_id=user.id,
            urgency=3,
            impact=3,
            source="web",
            status="new",
        )
        clean_session.add(incident)
        await clean_session.commit()

        comment = CommentModel(
            incident_id=incident.id,
            user_id=user.id,
            content="Test comment",
            is_internal=False,
        )
        clean_session.add(comment)
        await clean_session.commit()

        result = await clean_session.execute(
            select(CommentModel).where(CommentModel.incident_id == incident.id)
        )
        comments = result.scalars().all()
        assert len(comments) >= 1

    @pytest.mark.asyncio
    async def test_rollback_on_error(self, clean_session):
        """Verificar rollback explícito."""
        user = UserModel(
            username="rb_user",
            email="rb@test.com",
            hashed_password="$2b$12$test_hash",
        )
        clean_session.add(user)
        await clean_session.commit()
        user_id = user.id

        try:
            user2 = UserModel(
                username="rb_user2",
                email="rb2@test.com",
                hashed_password="$2b$12$test_hash",
            )
            clean_session.add(user2)
            await clean_session.flush()
            raise RuntimeError("Error forzado")
        except RuntimeError:
            await clean_session.rollback()

        u1 = await clean_session.get(UserModel, user_id)
        assert u1 is not None, "user1 debe persistir"

        result = await clean_session.execute(
            select(UserModel).where(UserModel.username == "rb_user2")
        )
        u2 = result.scalars().first()
        assert u2 is None, "user2 no debe persistir (rollback)"

    @pytest.mark.asyncio
    async def test_engine_url_is_sqlite_dev(self, engine):
        """Verificar que el engine usa SQLite."""
        url_str = str(engine.url)
        assert "sqlite" in url_str, f"Esperado SQLite, obtenido: {url_str}"
        assert "aiosqlite" in url_str, f"Debe ser async, obtenido: {url_str}"
