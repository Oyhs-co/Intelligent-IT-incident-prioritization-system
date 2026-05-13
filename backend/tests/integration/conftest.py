"""Integration tests configuration."""

import asyncio
import os
from collections.abc import AsyncGenerator

import pytest

# DATABASE_URL was already set by root conftest to a file-based SQLite
# All engines (test + app) share the same file


@pytest.fixture(autouse=True)
def _patch_passlib():
    """Parchea passlib bcrypt para evitar error de compatibilidad."""
    from src.domain.entities.user import pwd_context
    original_hash = pwd_context.hash
    original_verify = pwd_context.verify
    def _mock_hash(secret, **kwds):
        if isinstance(secret, str):
            secret = secret.encode("utf-8")
        return f"$2b$12${secret.hex()}$mockhash1234567890abc"
    def _mock_verify(secret, hash, **kwds):
        expected = _mock_hash(secret)
        return hash == expected
    pwd_context.hash = _mock_hash
    pwd_context.verify = _mock_verify
    yield
    pwd_context.hash = original_hash
    pwd_context.verify = original_verify


@pytest.fixture(autouse=True)
def _patch_rate_limit(monkeypatch):
    """Desactiva rate limiting en tests parcheando el método de verificación."""
    from src.presentation.api.middleware.rate_limit_middleware import (
        RateLimitMiddleware,
    )
    async def _always_allowed(self, client_ip, now):
        return (True, "")
    monkeypatch.setattr(RateLimitMiddleware, "_check_limits", _always_allowed)
    yield


from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.database import Base, get_db_session
from src.infrastructure.database.repositories import IncidentRepository, UserRepository
from src.presentation.api.app import app

TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture(scope="session", autouse=True)
async def _init_app_db(event_loop):
    """Ensure app's engine creates tables in the shared database."""
    from src.infrastructure.database import init_db
    try:
        await init_db()
    except Exception as e:
        print(f"init_db warning: {e}")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop."""
    loop = asyncio.new_event_loop()
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
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden DB session."""
    async def _override_session():
        yield session
    app.dependency_overrides[get_db_session] = _override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


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
    from src.domain.entities.incident import Incident
    from src.domain.value_objects import IncidentSource, IncidentStatus
    from src.infrastructure.database.repositories import IncidentRepository

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
