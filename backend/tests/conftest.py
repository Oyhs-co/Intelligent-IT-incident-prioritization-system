"""Tests configuration."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Create temp file-based SQLite so all engines share the same database
_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_db_path = _db_file.name
_db_file.close()
_db_uri = f"sqlite+aiosqlite:///{_db_path}"

os.environ["DATABASE_URL"] = _db_uri

import atexit


def _cleanup_db():
    for f in (_db_path, _db_path + "-wal", _db_path + "-shm"):
        try:
            if os.path.exists(f):
                os.unlink(f)
        except (PermissionError, OSError):
            pass

# Try to close app's engine before atexit cleanup
import atexit
atexit.register(_cleanup_db)


import pytest
import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from src.presentation.api.app import app
from src.infrastructure.database import Base


TEST_DATABASE_URL = _db_uri


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def _close_app_engine():
    """Close app's engine after all tests so file can be cleaned up."""
    yield
    from src.infrastructure.database import close_db
    try:
        await close_db()
    except Exception:
        pass


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
