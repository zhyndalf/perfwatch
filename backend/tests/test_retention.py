"""Tests for retention policy API endpoints."""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.metrics import MetricsSnapshot
from app.services.auth import create_access_token, hash_password


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        username="retentionuser",
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    return create_access_token({"sub": str(test_user.id)})


class TestRetentionPolicy:
    """Tests for retention policy endpoints."""

    @pytest.mark.asyncio
    async def test_get_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/retention")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_policy_creates_default(
        self, client: AsyncClient, auth_token: str
    ):
        response = await client.get(
            "/api/retention",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["retention_days"] == 30
        assert data["archive_enabled"] is True
        assert data["downsample_after_days"] == 7
        assert data["downsample_interval"] in {"1h", "1 hour"}

    @pytest.mark.asyncio
    async def test_update_rejects_invalid_interval(
        self, client: AsyncClient, auth_token: str
    ):
        response = await client.put(
            "/api/retention",
            json={"downsample_interval": "2h"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_rejects_invalid_downsample_days(
        self, client: AsyncClient, auth_token: str
    ):
        response = await client.put(
            "/api/retention",
            json={"retention_days": 7, "downsample_after_days": 14},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_policy(
        self, client: AsyncClient, auth_token: str
    ):
        response = await client.put(
            "/api/retention",
            json={
                "retention_days": 14,
                "archive_enabled": False,
                "downsample_after_days": 7,
                "downsample_interval": "1h",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["retention_days"] == 14
        assert data["archive_enabled"] is False
        assert data["downsample_after_days"] == 7
        assert data["downsample_interval"] == "1h"


class TestRetentionCleanup:
    """Tests for retention cleanup endpoint."""

    @pytest.mark.asyncio
    async def test_cleanup_deletes_expired(
        self,
        client: AsyncClient,
        auth_token: str,
        db_session: AsyncSession,
    ):
        now = datetime.now(timezone.utc)
        db_session.add(
            MetricsSnapshot(
                timestamp=now - timedelta(days=2),
                metric_type="cpu",
                metric_data={"usage_percent": 50.0},
            )
        )
        db_session.add(
            MetricsSnapshot(
                timestamp=now - timedelta(hours=1),
                metric_type="cpu",
                metric_data={"usage_percent": 60.0},
            )
        )
        await db_session.commit()

        await client.put(
            "/api/retention",
            json={"retention_days": 1, "downsample_after_days": 1},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        response = await client.post(
            "/api/retention/cleanup",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 1

        result = await db_session.execute(select(MetricsSnapshot))
        remaining = result.scalars().all()
        assert len(remaining) == 1
