"""Integration tests configuration."""

import pytest
import asyncio
from typing import AsyncGenerator
from datetime import datetime
from uuid import UUID, uuid4


@pytest.fixture(autouse=True)
def _patch_passlib():
    """Parchea passlib bcrypt para evitar error de compatibilidad."""
    from src.domain.entities.user import pwd_context
    original_hash = pwd_context.hash
    def _mock_hash(secret, **kwds):
        if isinstance(secret, str):
            secret = secret.encode("utf-8")
        return f"$2b$12${secret.hex()}$mockhash1234567890abc"
    pwd_context.hash = _mock_hash
    yield
    pwd_context.hash = original_hash

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from src.presentation.api.app import app
from src.infrastructure.database import Base
from src.infrastructure.database.models import UserModel, IncidentModel
from src.infrastructure.database.repositories import IncidentRepository, UserRepository


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for a test."""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


_user_counter = 0


@pytest.fixture
async def test_user(session: AsyncSession):
    """Create a test user."""
    global _user_counter
    _user_counter += 1
    from src.domain.entities.user import User
    from src.infrastructure.database.repositories import UserRepository

    repo = UserRepository(session)
    entity = User()
    entity.email = f"test{_user_counter}@example.com"
    entity.username = f"testuser{_user_counter}"
    entity.set_password("testpass123")

    created = await repo.create(entity)
    await session.commit()
    return created


@pytest.fixture
async def test_incident(session: AsyncSession, test_user):
    """Create a test incident."""
    from src.infrastructure.database.repositories import IncidentRepository
    from src.domain.entities.incident import Incident
    from src.domain.value_objects import IncidentStatus, IncidentSource

    repo = IncidentRepository(session)
    entity = Incident()
    entity.title = "Test Incident"
    entity.description = "Test description for integration testing"
    entity.status = IncidentStatus.OPEN
    entity.urgency = 3
    entity.impact = 3
    entity.source = IncidentSource.WEB
    entity.reporter_id = test_user.id

    created = await repo.create(entity)
    await session.commit()
    return created


@pytest.fixture
async def incident_repository(session: AsyncSession) -> IncidentRepository:
    """Create an incident repository."""
    return IncidentRepository(session)


@pytest.fixture
async def user_repository(session: AsyncSession) -> UserRepository:
    """Create a user repository."""
    return UserRepository(session)
