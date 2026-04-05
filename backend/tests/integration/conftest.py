"""Integration tests configuration."""

import pytest
import asyncio
from typing import AsyncGenerator
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient

from src.presentation.api.app import app
from src.infrastructure.database.models import Base, UserModel, IncidentModel
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
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(session: AsyncSession) -> UserModel:
    """Create a test user."""
    user = UserModel(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$test_hash",
        role="user",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
async def test_incident(session: AsyncSession, test_user) -> IncidentModel:
    """Create a test incident."""
    incident = IncidentModel(
        id=uuid4(),
        ticket_number="INC-001",
        title="Test Incident",
        description="Test description for integration testing",
        status="open",
        urgency=3,
        impact=3,
        source="web",
        reporter_id=test_user.id,
    )
    session.add(incident)
    await session.commit()
    await session.refresh(incident)
    return incident


@pytest.fixture
async def incident_repository(session: AsyncSession) -> IncidentRepository:
    """Create an incident repository."""
    return IncidentRepository(session)


@pytest.fixture
async def user_repository(session: AsyncSession) -> UserRepository:
    """Create a user repository."""
    return UserRepository(session)
