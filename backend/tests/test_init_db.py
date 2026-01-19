"""Tests for init_db script."""

import pytest
from sqlalchemy import select

from app.models import User, Config, ArchivePolicy
from app.init_db import (
    create_default_admin,
    create_default_config,
    create_default_archive_policy,
)


class TestCreateDefaultAdmin:
    """Tests for default admin user creation."""

    @pytest.mark.asyncio
    async def test_creates_admin_user(self, db_session):
        """Test that admin user is created."""
        await create_default_admin(db_session)

        result = await db_session.execute(
            select(User).where(User.username == "admin")
        )
        user = result.scalar_one_or_none()

        assert user is not None
        assert user.username == "admin"
        assert user.password_hash is not None
        assert len(user.password_hash) > 0

    @pytest.mark.asyncio
    async def test_admin_password_is_hashed(self, db_session):
        """Test that admin password is bcrypt hashed, not plaintext."""
        await create_default_admin(db_session)

        result = await db_session.execute(
            select(User).where(User.username == "admin")
        )
        user = result.scalar_one()

        # bcrypt hashes start with $2b$ or $2a$
        assert user.password_hash.startswith("$2")
        assert user.password_hash != "admin123"  # Not plaintext

    @pytest.mark.asyncio
    async def test_does_not_duplicate_admin(self, db_session):
        """Test that calling twice doesn't create duplicate admin."""
        await create_default_admin(db_session)
        await create_default_admin(db_session)

        result = await db_session.execute(
            select(User).where(User.username == "admin")
        )
        users = result.scalars().all()

        assert len(users) == 1


class TestCreateDefaultConfig:
    """Tests for default config creation."""

    @pytest.mark.asyncio
    async def test_creates_sampling_config(self, db_session):
        """Test that sampling config is created."""
        await create_default_config(db_session)

        result = await db_session.execute(
            select(Config).where(Config.key == "sampling")
        )
        config = result.scalar_one_or_none()

        assert config is not None
        assert "interval_seconds" in config.value

    @pytest.mark.asyncio
    async def test_creates_retention_config(self, db_session):
        """Test that retention config is created."""
        await create_default_config(db_session)

        result = await db_session.execute(
            select(Config).where(Config.key == "retention")
        )
        config = result.scalar_one_or_none()

        assert config is not None
        assert "days" in config.value
        assert "archive_enabled" in config.value

    @pytest.mark.asyncio
    async def test_creates_features_config(self, db_session):
        """Test that features config is created."""
        await create_default_config(db_session)

        result = await db_session.execute(
            select(Config).where(Config.key == "features")
        )
        config = result.scalar_one_or_none()

        assert config is not None
        assert "perf_events_enabled" in config.value

    @pytest.mark.asyncio
    async def test_does_not_duplicate_config(self, db_session):
        """Test that calling twice doesn't create duplicates."""
        await create_default_config(db_session)
        await create_default_config(db_session)

        result = await db_session.execute(select(Config))
        configs = result.scalars().all()

        assert len(configs) == 3  # sampling, retention, features


class TestCreateDefaultArchivePolicy:
    """Tests for default archive policy creation."""

    @pytest.mark.asyncio
    async def test_creates_archive_policy(self, db_session):
        """Test that archive policy is created."""
        await create_default_archive_policy(db_session)

        result = await db_session.execute(select(ArchivePolicy))
        policy = result.scalar_one_or_none()

        assert policy is not None
        assert policy.retention_days == 30
        assert policy.archive_enabled is True

    @pytest.mark.asyncio
    async def test_does_not_duplicate_policy(self, db_session):
        """Test that calling twice doesn't create duplicates."""
        await create_default_archive_policy(db_session)
        await create_default_archive_policy(db_session)

        result = await db_session.execute(select(ArchivePolicy))
        policies = result.scalars().all()

        assert len(policies) == 1
