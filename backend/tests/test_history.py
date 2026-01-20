"""Tests for history storage and API endpoints."""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.metrics import MetricsSnapshot
from app.services.auth import hash_password, create_access_token
from app.services.metrics_storage import (
    save_metrics_snapshot,
    save_all_metrics,
    query_metrics_history,
    get_latest_metrics,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user for authentication."""
    user = User(
        username="historyuser",
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Get an auth token for the test user."""
    return create_access_token({"sub": str(test_user.id)})


@pytest_asyncio.fixture
async def sample_metrics(db_session: AsyncSession) -> list[MetricsSnapshot]:
    """Create sample metrics data for testing."""
    base_time = datetime.now(timezone.utc) - timedelta(hours=1)
    snapshots = []

    for i in range(10):
        timestamp = base_time + timedelta(minutes=i * 5)

        # CPU metrics
        cpu = MetricsSnapshot(
            timestamp=timestamp,
            metric_type="cpu",
            metric_data={
                "usage_percent": 40.0 + i * 2,
                "per_core": [35.0 + i, 45.0 + i, 38.0 + i, 42.0 + i],
                "user": 25.0 + i,
                "system": 15.0 + i,
            },
        )
        db_session.add(cpu)
        snapshots.append(cpu)

        # Memory metrics
        memory = MetricsSnapshot(
            timestamp=timestamp,
            metric_type="memory",
            metric_data={
                "usage_percent": 60.0 + i,
                "total_bytes": 16 * 1024 * 1024 * 1024,
                "used_bytes": (10 + i // 2) * 1024 * 1024 * 1024,
                "available_bytes": (6 - i // 2) * 1024 * 1024 * 1024,
            },
        )
        db_session.add(memory)
        snapshots.append(memory)

    await db_session.commit()
    for s in snapshots:
        await db_session.refresh(s)
    return snapshots


# =============================================================================
# Metrics Storage Service Tests
# =============================================================================


class TestSaveMetricsSnapshot:
    """Tests for save_metrics_snapshot function."""

    @pytest.mark.asyncio
    async def test_save_single_snapshot(self, db_session: AsyncSession):
        """Save a single metrics snapshot."""
        timestamp = datetime.now(timezone.utc)
        metric_data = {"usage_percent": 45.5, "per_core": [40.0, 50.0]}

        snapshot = await save_metrics_snapshot(
            timestamp=timestamp,
            metric_type="cpu",
            metric_data=metric_data,
            session=db_session,
        )

        assert snapshot.id is not None
        assert snapshot.metric_type == "cpu"
        assert snapshot.metric_data == metric_data

    @pytest.mark.asyncio
    async def test_save_different_metric_types(self, db_session: AsyncSession):
        """Save snapshots for different metric types."""
        timestamp = datetime.now(timezone.utc)

        for metric_type in ["cpu", "memory", "network", "disk"]:
            await save_metrics_snapshot(
                timestamp=timestamp,
                metric_type=metric_type,
                metric_data={"test": f"{metric_type}_data"},
                session=db_session,
            )

        # Verify all were saved
        result = await db_session.execute(select(MetricsSnapshot))
        snapshots = result.scalars().all()
        assert len(snapshots) == 4


class TestSaveAllMetrics:
    """Tests for save_all_metrics function."""

    @pytest.mark.asyncio
    async def test_save_all_metrics_from_snapshot(self, db_session: AsyncSession):
        """Save all metrics from an aggregated snapshot."""
        snapshot_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {"usage_percent": 45.5},
            "memory": {"usage_percent": 60.0},
            "network": {"bytes_sent_per_sec": 1000},
            "disk": {"io": {"read_bytes_per_sec": 500}},
        }

        await save_all_metrics(snapshot_data, session=db_session)

        # Verify metrics were saved
        result = await db_session.execute(select(MetricsSnapshot))
        snapshots = result.scalars().all()
        assert len(snapshots) == 4

        # Verify each type
        types = {s.metric_type for s in snapshots}
        assert types == {"cpu", "memory", "network", "disk"}

    @pytest.mark.asyncio
    async def test_save_all_metrics_with_iso_z_timestamp(self, db_session: AsyncSession):
        """Save metrics with Z-suffix ISO timestamp."""
        snapshot_data = {
            "timestamp": "2026-01-20T12:00:00Z",
            "cpu": {"usage_percent": 50.0},
        }

        await save_all_metrics(snapshot_data, session=db_session)

        result = await db_session.execute(select(MetricsSnapshot))
        snapshot = result.scalar_one()
        assert snapshot.metric_type == "cpu"
        assert snapshot.timestamp.year == 2026

    @pytest.mark.asyncio
    async def test_save_all_metrics_skips_none_values(self, db_session: AsyncSession):
        """Skip saving metrics that are None."""
        snapshot_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {"usage_percent": 45.5},
            "memory": None,  # Should be skipped
            "network": {"bytes_sent_per_sec": 1000},
        }

        await save_all_metrics(snapshot_data, session=db_session)

        result = await db_session.execute(select(MetricsSnapshot))
        snapshots = result.scalars().all()
        assert len(snapshots) == 2
        types = {s.metric_type for s in snapshots}
        assert types == {"cpu", "network"}


class TestQueryMetricsHistory:
    """Tests for query_metrics_history function."""

    @pytest.mark.asyncio
    async def test_query_by_time_range(
        self, db_session: AsyncSession, sample_metrics: list[MetricsSnapshot]
    ):
        """Query metrics within a time range."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=2)
        end_time = datetime.now(timezone.utc)

        results, _ = await query_metrics_history(
            metric_type="cpu",
            start_time=start_time,
            end_time=end_time,
            session=db_session,
        )

        assert len(results) == 10  # All CPU snapshots
        assert all(r.metric_type == "cpu" for r in results)

    @pytest.mark.asyncio
    async def test_query_by_metric_type(
        self, db_session: AsyncSession, sample_metrics: list[MetricsSnapshot]
    ):
        """Query filters by metric type correctly."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=2)
        end_time = datetime.now(timezone.utc)

        cpu_results, _ = await query_metrics_history(
            metric_type="cpu",
            start_time=start_time,
            end_time=end_time,
            session=db_session,
        )

        memory_results, _ = await query_metrics_history(
            metric_type="memory",
            start_time=start_time,
            end_time=end_time,
            session=db_session,
        )

        assert len(cpu_results) == 10
        assert len(memory_results) == 10
        assert cpu_results[0].metric_type == "cpu"
        assert memory_results[0].metric_type == "memory"

    @pytest.mark.asyncio
    async def test_query_with_limit(
        self, db_session: AsyncSession, sample_metrics: list[MetricsSnapshot]
    ):
        """Query respects limit parameter."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=2)
        end_time = datetime.now(timezone.utc)

        results, _ = await query_metrics_history(
            metric_type="cpu",
            start_time=start_time,
            end_time=end_time,
            limit=5,
            session=db_session,
        )

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_query_empty_range(self, db_session: AsyncSession):
        """Query returns empty list for range with no data."""
        start_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2020, 1, 2, tzinfo=timezone.utc)

        results, _ = await query_metrics_history(
            metric_type="cpu",
            start_time=start_time,
            end_time=end_time,
            session=db_session,
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_query_ordered_by_timestamp(
        self, db_session: AsyncSession, sample_metrics: list[MetricsSnapshot]
    ):
        """Results are ordered by timestamp ascending."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=2)
        end_time = datetime.now(timezone.utc)

        results, _ = await query_metrics_history(
            metric_type="cpu",
            start_time=start_time,
            end_time=end_time,
            session=db_session,
        )

        timestamps = [r.timestamp for r in results]
        assert timestamps == sorted(timestamps)

    @pytest.mark.asyncio
    async def test_query_with_interval_downsampling(self, db_session: AsyncSession):
        """Downsample results when interval is provided."""
        base_time = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)

        for i in range(6):
            snapshot = MetricsSnapshot(
                timestamp=base_time + timedelta(minutes=i * 10),
                metric_type="cpu",
                metric_data={"usage_percent": float(i * 10)},
            )
            db_session.add(snapshot)

        await db_session.commit()

        results, interval_label = await query_metrics_history(
            metric_type="cpu",
            start_time=base_time,
            end_time=base_time + timedelta(minutes=59),
            interval="1h",
            session=db_session,
        )

        assert interval_label == "1h"
        assert len(results) == 1
        assert abs(results[0].metric_data["usage_percent"] - 25.0) < 0.01


class TestGetLatestMetrics:
    """Tests for get_latest_metrics function."""

    @pytest.mark.asyncio
    async def test_get_latest_single(
        self, db_session: AsyncSession, sample_metrics: list[MetricsSnapshot]
    ):
        """Get the most recent metric."""
        results = await get_latest_metrics(
            metric_type="cpu",
            limit=1,
            session=db_session,
        )

        assert len(results) == 1
        # Should have the highest usage (last sample created)
        assert results[0].metric_data["usage_percent"] == 58.0  # 40 + 9*2

    @pytest.mark.asyncio
    async def test_get_latest_multiple(
        self, db_session: AsyncSession, sample_metrics: list[MetricsSnapshot]
    ):
        """Get multiple recent metrics."""
        results = await get_latest_metrics(
            metric_type="memory",
            limit=3,
            session=db_session,
        )

        assert len(results) == 3
        # Should be in descending order
        timestamps = [r.timestamp for r in results]
        assert timestamps == sorted(timestamps, reverse=True)


# =============================================================================
# History API Tests
# =============================================================================


class TestHistoryEndpoint:
    """Tests for GET /api/history/metrics endpoint."""

    @pytest.mark.asyncio
    async def test_query_requires_auth(self, client: AsyncClient):
        """Request without token returns 401."""
        response = await client.get(
            "/api/history/metrics",
            params={
                "metric_type": "cpu",
                "start_time": "2026-01-20T00:00:00Z",
                "end_time": "2026-01-20T23:59:59Z",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_query_valid_request(
        self,
        client: AsyncClient,
        auth_token: str,
        sample_metrics: list[MetricsSnapshot],
    ):
        """Valid authenticated request returns data."""
        start_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        end_time = datetime.now(timezone.utc).isoformat()

        response = await client.get(
            "/api/history/metrics",
            params={
                "metric_type": "cpu",
                "start_time": start_time,
                "end_time": end_time,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["metric_type"] == "cpu"
        assert data["count"] == 10
        assert len(data["data_points"]) == 10

    @pytest.mark.asyncio
    async def test_query_with_limit(
        self,
        client: AsyncClient,
        auth_token: str,
        sample_metrics: list[MetricsSnapshot],
    ):
        """Limit parameter restricts results."""
        start_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        end_time = datetime.now(timezone.utc).isoformat()

        response = await client.get(
            "/api/history/metrics",
            params={
                "metric_type": "cpu",
                "start_time": start_time,
                "end_time": end_time,
                "limit": 3,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["data_points"]) == 3

    @pytest.mark.asyncio
    async def test_query_invalid_metric_type(
        self, client: AsyncClient, auth_token: str
    ):
        """Invalid metric type returns 400."""
        response = await client.get(
            "/api/history/metrics",
            params={
                "metric_type": "invalid_type",
                "start_time": "2026-01-20T00:00:00Z",
                "end_time": "2026-01-20T23:59:59Z",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 400
        assert "Invalid metric_type" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_query_invalid_time_range(
        self, client: AsyncClient, auth_token: str
    ):
        """Start time after end time returns 400."""
        response = await client.get(
            "/api/history/metrics",
            params={
                "metric_type": "cpu",
                "start_time": "2026-01-20T23:59:59Z",
                "end_time": "2026-01-20T00:00:00Z",  # Before start
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 400
        assert "start_time must be before end_time" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_query_empty_result(
        self, client: AsyncClient, auth_token: str
    ):
        """Query with no matching data returns empty list."""
        response = await client.get(
            "/api/history/metrics",
            params={
                "metric_type": "cpu",
                "start_time": "2020-01-01T00:00:00Z",
                "end_time": "2020-01-02T00:00:00Z",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["data_points"] == []

    @pytest.mark.asyncio
    async def test_query_missing_required_params(
        self, client: AsyncClient, auth_token: str
    ):
        """Missing required parameters returns 422."""
        # Missing metric_type
        response = await client.get(
            "/api/history/metrics",
            params={
                "start_time": "2026-01-20T00:00:00Z",
                "end_time": "2026-01-20T23:59:59Z",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_data_point_structure(
        self,
        client: AsyncClient,
        auth_token: str,
        sample_metrics: list[MetricsSnapshot],
    ):
        """Data points have correct structure."""
        start_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        end_time = datetime.now(timezone.utc).isoformat()

        response = await client.get(
            "/api/history/metrics",
            params={
                "metric_type": "cpu",
                "start_time": start_time,
                "end_time": end_time,
                "limit": 1,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        point = data["data_points"][0]

        assert "timestamp" in point
        assert "data" in point
        assert "usage_percent" in point["data"]
        assert "per_core" in point["data"]


class TestMetricTypesEndpoint:
    """Tests for GET /api/history/metrics/types endpoint."""

    @pytest.mark.asyncio
    async def test_get_metric_types_requires_auth(self, client: AsyncClient):
        """Request without token returns 401."""
        response = await client.get("/api/history/metrics/types")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_metric_types(
        self, client: AsyncClient, auth_token: str
    ):
        """Returns list of available metric types."""
        response = await client.get(
            "/api/history/metrics/types",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "metric_types" in data
        assert "cpu" in data["metric_types"]
        assert "memory" in data["metric_types"]
        assert "network" in data["metric_types"]
        assert "disk" in data["metric_types"]
        assert "perf_events" in data["metric_types"]
        assert "memory_bandwidth" in data["metric_types"]


class TestHistoryCompareEndpoint:
    """Tests for GET /api/history/compare endpoint."""

    @pytest.mark.asyncio
    async def test_compare_requires_auth(self, client: AsyncClient):
        response = await client.get(
            "/api/history/compare",
            params={
                "metric_type": "cpu",
                "period": "hour",
                "compare_to": "yesterday",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_compare_invalid_params(self, client: AsyncClient, auth_token: str):
        response = await client.get(
            "/api/history/compare",
            params={
                "metric_type": "cpu",
                "period": "month",
                "compare_to": "yesterday",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        response = await client.get(
            "/api/history/compare",
            params={
                "metric_type": "cpu",
                "period": "hour",
                "compare_to": "last_month",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_compare_valid_request(
        self,
        client: AsyncClient,
        auth_token: str,
        db_session: AsyncSession,
    ):
        now = datetime.now(timezone.utc)
        base_time = now - timedelta(minutes=50)
        compare_shift = timedelta(days=1)

        for i in range(6):
            timestamp = base_time + timedelta(minutes=i * 10)
            db_session.add(
                MetricsSnapshot(
                    timestamp=timestamp,
                    metric_type="cpu",
                    metric_data={"usage_percent": 40.0 + i},
                )
            )
            db_session.add(
                MetricsSnapshot(
                    timestamp=timestamp - compare_shift,
                    metric_type="cpu",
                    metric_data={"usage_percent": 30.0 + i},
                )
            )

        await db_session.commit()

        response = await client.get(
            "/api/history/compare",
            params={
                "metric_type": "cpu",
                "period": "hour",
                "compare_to": "yesterday",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["metric_type"] == "cpu"
        assert data["period"] == "hour"
        assert data["compare_to"] == "yesterday"
        assert data["current"]["data_points"]
        assert data["comparison"]["data_points"]
        assert data["summary"]["current_avg"] is not None
        assert data["summary"]["comparison_avg"] is not None
