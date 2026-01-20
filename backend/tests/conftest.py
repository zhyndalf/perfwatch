"""Pytest configuration and fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db


# Use PostgreSQL test database (same as main db for simplicity in Docker)
# In production, you'd use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://perfwatch:perfwatch@db:5432/perfwatch_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create async engine for testing."""
    # First create the test database if it doesn't exist
    admin_engine = create_async_engine(
        "postgresql+asyncpg://perfwatch:perfwatch@db:5432/perfwatch",
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT",
    )

    async with admin_engine.connect() as conn:
        # Check if test database exists
        result = await conn.execute(
            __import__('sqlalchemy').text(
                "SELECT 1 FROM pg_database WHERE datname = 'perfwatch_test'"
            )
        )
        if not result.scalar():
            await conn.execute(
                __import__('sqlalchemy').text("CREATE DATABASE perfwatch_test")
            )

    await admin_engine.dispose()

    # Now connect to test database
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for testing."""
    async_session = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Create test client with database override."""
    from httpx import AsyncClient, ASGITransport
    os.environ.setdefault("BACKGROUND_COLLECTION_ENABLED", "false")
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
