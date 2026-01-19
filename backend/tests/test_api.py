"""Tests for API endpoints."""

import pytest


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "perfwatch-backend"


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.mark.asyncio
    async def test_root_returns_api_info(self, client):
        """Test root endpoint returns API information."""
        response = await client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"


class TestDBStatusEndpoint:
    """Tests for database status endpoint."""

    @pytest.mark.asyncio
    async def test_db_status_connected(self, client):
        """Test db-status endpoint when database is connected."""
        response = await client.get("/api/db-status")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "connected"
        assert data["database"] == "postgresql"
