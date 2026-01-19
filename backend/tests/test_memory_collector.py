"""Tests for the Memory collector."""

import pytest

from app.collectors.memory import MemoryCollector
from app.collectors.aggregator import MetricsAggregator


class TestMemoryCollector:
    """Tests for MemoryCollector class."""

    @pytest.mark.asyncio
    async def test_collect_returns_total_bytes(self):
        """Test that collect() returns total memory."""
        collector = MemoryCollector()
        data = await collector.collect()

        assert "total_bytes" in data
        assert isinstance(data["total_bytes"], int)
        assert data["total_bytes"] > 0

    @pytest.mark.asyncio
    async def test_collect_returns_available_bytes(self):
        """Test that collect() returns available memory."""
        collector = MemoryCollector()
        data = await collector.collect()

        assert "available_bytes" in data
        assert isinstance(data["available_bytes"], int)
        assert data["available_bytes"] > 0
        assert data["available_bytes"] <= data["total_bytes"]

    @pytest.mark.asyncio
    async def test_collect_returns_used_bytes(self):
        """Test that collect() returns used memory."""
        collector = MemoryCollector()
        data = await collector.collect()

        assert "used_bytes" in data
        assert isinstance(data["used_bytes"], int)
        assert data["used_bytes"] >= 0

    @pytest.mark.asyncio
    async def test_collect_returns_usage_percent(self):
        """Test that collect() returns usage percentage."""
        collector = MemoryCollector()
        data = await collector.collect()

        assert "usage_percent" in data
        assert isinstance(data["usage_percent"], (int, float))
        assert 0 <= data["usage_percent"] <= 100

    @pytest.mark.asyncio
    async def test_collect_returns_swap_info(self):
        """Test that collect() returns swap information."""
        collector = MemoryCollector()
        data = await collector.collect()

        assert "swap_total_bytes" in data
        assert "swap_used_bytes" in data
        assert "swap_free_bytes" in data
        assert "swap_percent" in data

        # Swap can be 0 if not configured
        assert data["swap_total_bytes"] >= 0
        assert data["swap_used_bytes"] >= 0
        assert 0 <= data["swap_percent"] <= 100

    @pytest.mark.asyncio
    async def test_collect_handles_linux_specific_fields(self):
        """Test that Linux-specific fields are present (may be None)."""
        collector = MemoryCollector()
        data = await collector.collect()

        # These should exist but may be None on non-Linux systems
        assert "buffers_bytes" in data
        assert "cached_bytes" in data
        assert "shared_bytes" in data

    @pytest.mark.asyncio
    async def test_safe_collect_adds_metadata(self):
        """Test that safe_collect adds timestamp and error fields."""
        collector = MemoryCollector()
        data = await collector.safe_collect()

        assert "_timestamp" in data
        assert "_error" in data
        assert data["_error"] is None

    @pytest.mark.asyncio
    async def test_disabled_collector(self):
        """Test that disabled collector returns disabled status."""
        collector = MemoryCollector(enabled=False)
        data = await collector.safe_collect()

        assert data["_enabled"] is False
        assert "total_bytes" not in data

    def test_collector_name(self):
        """Test that collector has correct name."""
        collector = MemoryCollector()
        assert collector.name == "memory"

    def test_collector_repr(self):
        """Test collector string representation."""
        collector = MemoryCollector()
        repr_str = repr(collector)

        assert "MemoryCollector" in repr_str
        assert "memory" in repr_str


class TestMemoryCollectorIntegration:
    """Integration tests with the aggregator."""

    @pytest.mark.asyncio
    async def test_with_aggregator(self):
        """Test Memory collector works with MetricsAggregator."""
        memory_collector = MemoryCollector()
        aggregator = MetricsAggregator(collectors=[memory_collector])

        snapshot = await aggregator.collect_all()

        assert "timestamp" in snapshot
        assert "memory" in snapshot
        assert snapshot["memory"]["_error"] is None
        assert "total_bytes" in snapshot["memory"]
        assert "usage_percent" in snapshot["memory"]

    @pytest.mark.asyncio
    async def test_multiple_collections(self):
        """Test multiple consecutive collections work correctly."""
        collector = MemoryCollector()

        # Collect multiple times
        results = []
        for _ in range(3):
            data = await collector.collect()
            results.append(data)

        # All should have valid data
        for result in results:
            assert "total_bytes" in result
            assert "usage_percent" in result
            # Total memory should be consistent
            assert result["total_bytes"] == results[0]["total_bytes"]
