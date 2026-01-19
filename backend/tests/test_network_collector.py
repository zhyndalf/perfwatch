"""Tests for the Network collector."""

import pytest

from app.collectors.network import NetworkCollector
from app.collectors.aggregator import MetricsAggregator


class TestNetworkCollector:
    """Tests for NetworkCollector class."""

    @pytest.mark.asyncio
    async def test_collect_returns_total_bytes(self):
        """Test that collect() returns total bytes sent/received."""
        collector = NetworkCollector()
        data = await collector.collect()

        assert "total_bytes_sent" in data
        assert "total_bytes_recv" in data
        assert isinstance(data["total_bytes_sent"], int)
        assert isinstance(data["total_bytes_recv"], int)
        assert data["total_bytes_sent"] >= 0
        assert data["total_bytes_recv"] >= 0

    @pytest.mark.asyncio
    async def test_collect_returns_rates(self):
        """Test that collect() returns byte rates."""
        collector = NetworkCollector()
        data = await collector.collect()

        assert "bytes_sent_per_sec" in data
        assert "bytes_recv_per_sec" in data
        assert isinstance(data["bytes_sent_per_sec"], (int, float))
        assert isinstance(data["bytes_recv_per_sec"], (int, float))
        # First call should have 0 rates (no previous data)
        assert data["bytes_sent_per_sec"] >= 0
        assert data["bytes_recv_per_sec"] >= 0

    @pytest.mark.asyncio
    async def test_collect_returns_packets(self):
        """Test that collect() returns packet counts."""
        collector = NetworkCollector()
        data = await collector.collect()

        assert "packets_sent" in data
        assert "packets_recv" in data
        assert data["packets_sent"] >= 0
        assert data["packets_recv"] >= 0

    @pytest.mark.asyncio
    async def test_collect_returns_errors(self):
        """Test that collect() returns error counts."""
        collector = NetworkCollector()
        data = await collector.collect()

        assert "errors_in" in data
        assert "errors_out" in data
        assert "drops_in" in data
        assert "drops_out" in data

    @pytest.mark.asyncio
    async def test_collect_returns_interfaces(self):
        """Test that collect() returns interface list."""
        collector = NetworkCollector()
        data = await collector.collect()

        assert "interfaces" in data
        assert isinstance(data["interfaces"], list)
        # Should have at least one interface (excluding loopback)

    @pytest.mark.asyncio
    async def test_collect_returns_connection_count(self):
        """Test that collect() returns connection count."""
        collector = NetworkCollector()
        data = await collector.collect()

        assert "connection_count" in data
        # May be -1 if permission denied
        assert isinstance(data["connection_count"], int)

    @pytest.mark.asyncio
    async def test_rate_calculation_on_second_call(self):
        """Test that rates are calculated on second call."""
        collector = NetworkCollector()

        # First call initializes
        await collector.collect()

        # Second call should calculate rates
        data = await collector.collect()

        # Rates should be non-negative
        assert data["bytes_sent_per_sec"] >= 0
        assert data["bytes_recv_per_sec"] >= 0

    @pytest.mark.asyncio
    async def test_safe_collect_adds_metadata(self):
        """Test that safe_collect adds timestamp and error fields."""
        collector = NetworkCollector()
        data = await collector.safe_collect()

        assert "_timestamp" in data
        assert "_error" in data
        assert data["_error"] is None

    @pytest.mark.asyncio
    async def test_disabled_collector(self):
        """Test that disabled collector returns disabled status."""
        collector = NetworkCollector(enabled=False)
        data = await collector.safe_collect()

        assert data["_enabled"] is False
        assert "total_bytes_sent" not in data

    def test_collector_name(self):
        """Test that collector has correct name."""
        collector = NetworkCollector()
        assert collector.name == "network"


class TestNetworkCollectorIntegration:
    """Integration tests with the aggregator."""

    @pytest.mark.asyncio
    async def test_with_aggregator(self):
        """Test Network collector works with MetricsAggregator."""
        network_collector = NetworkCollector()
        aggregator = MetricsAggregator(collectors=[network_collector])

        snapshot = await aggregator.collect_all()

        assert "timestamp" in snapshot
        assert "network" in snapshot
        assert snapshot["network"]["_error"] is None
        assert "total_bytes_sent" in snapshot["network"]

    @pytest.mark.asyncio
    async def test_multiple_collections(self):
        """Test multiple consecutive collections work correctly."""
        collector = NetworkCollector()

        # Collect multiple times
        results = []
        for _ in range(3):
            data = await collector.collect()
            results.append(data)

        # All should have valid data
        for result in results:
            assert "total_bytes_sent" in result
            assert "interfaces" in result
