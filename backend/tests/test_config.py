"""Tests for config API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.services.auth import create_access_token, hash_password


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        username="configuser",
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    return create_access_token({"sub": str(test_user.id)})


class TestConfigEndpoints:
    """Tests for /api/config endpoints."""

    @pytest.mark.asyncio
    async def test_get_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/config")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_config(self, client: AsyncClient, auth_token: str):
        response = await client.get(
            "/api/config",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "sampling_interval_seconds" in data
        assert "perf_events_enabled" in data
        assert "retention_days" in data
        assert "downsample_after_days" in data
        assert "downsample_interval" in data
        assert "app_version" in data

    @pytest.mark.asyncio
    async def test_update_config_sampling_interval(
        self, client: AsyncClient, auth_token: str
    ):
        response = await client.put(
            "/api/config",
            json={"sampling_interval_seconds": 10},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()["config"]
        assert data["sampling_interval_seconds"] == 10
