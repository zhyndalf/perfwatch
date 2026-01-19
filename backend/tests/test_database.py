"""Tests for database connection and session management."""

import pytest
from sqlalchemy import text


class TestDatabaseConnection:
    """Tests for database connection."""

    @pytest.mark.asyncio
    async def test_session_connects(self, db_session):
        """Test that database session can execute queries."""
        result = await db_session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1

    @pytest.mark.asyncio
    async def test_tables_created(self, db_session):
        """Test that all tables are created."""
        # PostgreSQL uses information_schema
        result = await db_session.execute(
            text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
        )
        tables = {row[0] for row in result.fetchall()}

        expected_tables = {"users", "metrics_snapshot", "config", "archive_policy"}
        assert expected_tables.issubset(tables)

    @pytest.mark.asyncio
    async def test_session_rollback_on_error(self, db_session):
        """Test that session rolls back on error."""
        from app.models import User

        # Add a user
        user = User(username="rollback_test", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        # Try to add duplicate (should fail)
        user2 = User(username="rollback_test", password_hash="hash2")
        db_session.add(user2)

        with pytest.raises(Exception):
            await db_session.commit()

        # Session should still be usable after rollback
        await db_session.rollback()
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
