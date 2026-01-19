"""Tests for database models."""

import pytest
from datetime import datetime, timezone
from sqlalchemy import select

from app.models import User, MetricsSnapshot, Config, ArchivePolicy


class TestUserModel:
    """Tests for User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            username="testuser",
            password_hash="hashed_password_123",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.password_hash == "hashed_password_123"
        assert user.created_at is not None
        assert user.last_login is None

    @pytest.mark.asyncio
    async def test_user_username_unique(self, db_session):
        """Test that username must be unique."""
        user1 = User(username="uniqueuser", password_hash="hash1")
        db_session.add(user1)
        await db_session.commit()

        user2 = User(username="uniqueuser", password_hash="hash2")
        db_session.add(user2)

        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_repr(self, db_session):
        """Test user string representation."""
        user = User(username="repruser", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        assert "repruser" in repr(user)
        assert str(user.id) in repr(user)


class TestMetricsSnapshotModel:
    """Tests for MetricsSnapshot model."""

    @pytest.mark.asyncio
    async def test_create_metrics_snapshot(self, db_session):
        """Test creating a metrics snapshot."""
        now = datetime.now(timezone.utc)
        snapshot = MetricsSnapshot(
            timestamp=now,
            metric_type="cpu",
            metric_data={
                "usage_percent": 45.2,
                "per_core": [40.1, 50.3, 42.8, 47.6],
            },
        )
        db_session.add(snapshot)
        await db_session.commit()
        await db_session.refresh(snapshot)

        assert snapshot.id is not None
        assert snapshot.metric_type == "cpu"
        assert snapshot.metric_data["usage_percent"] == 45.2
        assert len(snapshot.metric_data["per_core"]) == 4

    @pytest.mark.asyncio
    async def test_metrics_snapshot_query_by_type(self, db_session):
        """Test querying metrics by type."""
        now = datetime.now(timezone.utc)

        # Create CPU and memory snapshots
        cpu_snapshot = MetricsSnapshot(
            timestamp=now,
            metric_type="cpu",
            metric_data={"usage_percent": 50.0},
        )
        memory_snapshot = MetricsSnapshot(
            timestamp=now,
            metric_type="memory",
            metric_data={"usage_percent": 60.0},
        )
        db_session.add_all([cpu_snapshot, memory_snapshot])
        await db_session.commit()

        # Query only CPU metrics
        result = await db_session.execute(
            select(MetricsSnapshot).where(MetricsSnapshot.metric_type == "cpu")
        )
        cpu_metrics = result.scalars().all()

        assert len(cpu_metrics) == 1
        assert cpu_metrics[0].metric_data["usage_percent"] == 50.0

    @pytest.mark.asyncio
    async def test_metrics_snapshot_jsonb_nested(self, db_session):
        """Test storing and retrieving nested JSONB data."""
        now = datetime.now(timezone.utc)
        snapshot = MetricsSnapshot(
            timestamp=now,
            metric_type="network",
            metric_data={
                "interfaces": {
                    "eth0": {
                        "bytes_sent": 125000000,
                        "bytes_recv": 450000000,
                    }
                },
                "connections": {
                    "tcp": {"established": 45},
                },
            },
        )
        db_session.add(snapshot)
        await db_session.commit()
        await db_session.refresh(snapshot)

        assert snapshot.metric_data["interfaces"]["eth0"]["bytes_sent"] == 125000000
        assert snapshot.metric_data["connections"]["tcp"]["established"] == 45


class TestConfigModel:
    """Tests for Config model."""

    @pytest.mark.asyncio
    async def test_create_config(self, db_session):
        """Test creating a config entry."""
        config = Config(
            key="sampling",
            value={"interval_seconds": 5},
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)

        assert config.key == "sampling"
        assert config.value["interval_seconds"] == 5
        assert config.updated_at is not None

    @pytest.mark.asyncio
    async def test_config_key_primary(self, db_session):
        """Test that config key is primary key."""
        config1 = Config(key="test_key", value={"v": 1})
        db_session.add(config1)
        await db_session.commit()

        # Try to insert duplicate key
        config2 = Config(key="test_key", value={"v": 2})
        db_session.add(config2)

        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_config_update_value(self, db_session):
        """Test updating config value."""
        config = Config(key="features", value={"enabled": False})
        db_session.add(config)
        await db_session.commit()

        # Update value
        result = await db_session.execute(
            select(Config).where(Config.key == "features")
        )
        config = result.scalar_one()
        config.value = {"enabled": True}
        await db_session.commit()
        await db_session.refresh(config)

        assert config.value["enabled"] is True


class TestArchivePolicyModel:
    """Tests for ArchivePolicy model."""

    @pytest.mark.asyncio
    async def test_create_archive_policy(self, db_session):
        """Test creating an archive policy."""
        policy = ArchivePolicy(
            retention_days=30,
            archive_enabled=True,
            downsample_after_days=7,
            downsample_interval="1 hour",
        )
        db_session.add(policy)
        await db_session.commit()
        await db_session.refresh(policy)

        assert policy.id is not None
        assert policy.retention_days == 30
        assert policy.archive_enabled is True
        assert policy.downsample_after_days == 7
        assert policy.downsample_interval == "1 hour"
        assert policy.last_archive_run is None
        assert policy.created_at is not None

    @pytest.mark.asyncio
    async def test_archive_policy_defaults(self, db_session):
        """Test archive policy default values."""
        policy = ArchivePolicy()
        db_session.add(policy)
        await db_session.commit()
        await db_session.refresh(policy)

        assert policy.retention_days == 30
        assert policy.archive_enabled is True
        assert policy.downsample_after_days == 7
        assert policy.downsample_interval == "1 hour"
