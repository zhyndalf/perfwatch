"""Tests for the Disk collector."""

import pytest

from app.collectors.disk import DiskCollector
from app.collectors.aggregator import MetricsAggregator


class TestDiskCollector:
    """Tests for DiskCollector class."""

    @pytest.mark.asyncio
    async def test_collect_returns_partitions(self):
        """Test that collect() returns partition info."""
        collector = DiskCollector()
        data = await collector.collect()

        assert "partitions" in data
        assert isinstance(data["partitions"], list)
        # Should have at least one partition (root)
        assert len(data["partitions"]) > 0

    @pytest.mark.asyncio
    async def test_partition_has_required_fields(self):
        """Test that partitions have required fields."""
        collector = DiskCollector()
        data = await collector.collect()

        for partition in data["partitions"]:
            assert "device" in partition
            assert "mountpoint" in partition
            assert "fstype" in partition
            assert "total_bytes" in partition
            assert "used_bytes" in partition
            assert "free_bytes" in partition
            assert "usage_percent" in partition

    @pytest.mark.asyncio
    async def test_partition_values_valid(self):
        """Test that partition values are valid."""
        collector = DiskCollector()
        data = await collector.collect()

        for partition in data["partitions"]:
            assert partition["total_bytes"] > 0
            assert partition["used_bytes"] >= 0
            assert partition["free_bytes"] >= 0
            assert 0 <= partition["usage_percent"] <= 100
            # Used + Free should approximately equal Total
            assert partition["used_bytes"] + partition["free_bytes"] <= partition["total_bytes"]

    @pytest.mark.asyncio
    async def test_collect_returns_io_stats(self):
        """Test that collect() returns I/O statistics."""
        collector = DiskCollector()
        data = await collector.collect()

        assert "io" in data
        io = data["io"]

        assert "read_bytes_per_sec" in io
        assert "write_bytes_per_sec" in io
        assert "read_bytes" in io
        assert "write_bytes" in io
        assert "read_count" in io
        assert "write_count" in io

    @pytest.mark.asyncio
    async def test_io_values_valid(self):
        """Test that I/O values are non-negative."""
        collector = DiskCollector()
        data = await collector.collect()

        io = data["io"]
        assert io["read_bytes_per_sec"] >= 0
        assert io["write_bytes_per_sec"] >= 0
        assert io["read_bytes"] >= 0
        assert io["write_bytes"] >= 0

    @pytest.mark.asyncio
    async def test_rate_calculation_on_second_call(self):
        """Test that I/O rates are calculated on second call."""
        collector = DiskCollector()

        # First call initializes
        await collector.collect()

        # Second call should calculate rates
        data = await collector.collect()

        # Rates should be non-negative
        assert data["io"]["read_bytes_per_sec"] >= 0
        assert data["io"]["write_bytes_per_sec"] >= 0

    @pytest.mark.asyncio
    async def test_safe_collect_adds_metadata(self):
        """Test that safe_collect adds timestamp and error fields."""
        collector = DiskCollector()
        data = await collector.safe_collect()

        assert "_timestamp" in data
        assert "_error" in data
        assert data["_error"] is None

    @pytest.mark.asyncio
    async def test_disabled_collector(self):
        """Test that disabled collector returns disabled status."""
        collector = DiskCollector(enabled=False)
        data = await collector.safe_collect()

        assert data["_enabled"] is False
        assert "partitions" not in data

    def test_collector_name(self):
        """Test that collector has correct name."""
        collector = DiskCollector()
        assert collector.name == "disk"


class TestDiskCollectorIntegration:
    """Integration tests with the aggregator."""

    @pytest.mark.asyncio
    async def test_with_aggregator(self):
        """Test Disk collector works with MetricsAggregator."""
        disk_collector = DiskCollector()
        aggregator = MetricsAggregator(collectors=[disk_collector])

        snapshot = await aggregator.collect_all()

        assert "timestamp" in snapshot
        assert "disk" in snapshot
        assert snapshot["disk"]["_error"] is None
        assert "partitions" in snapshot["disk"]
        assert "io" in snapshot["disk"]

    @pytest.mark.asyncio
    async def test_multiple_collections(self):
        """Test multiple consecutive collections work correctly."""
        collector = DiskCollector()

        # Collect multiple times
        results = []
        for _ in range(3):
            data = await collector.collect()
            results.append(data)

        # All should have valid data
        for result in results:
            assert "partitions" in result
            assert "io" in result

    @pytest.mark.asyncio
    async def test_all_collectors_together(self):
        """Test all collectors work together in aggregator."""
        from app.collectors import CPUCollector, MemoryCollector, NetworkCollector

        aggregator = MetricsAggregator(
            collectors=[
                CPUCollector(),
                MemoryCollector(),
                NetworkCollector(),
                DiskCollector(),
            ]
        )

        snapshot = await aggregator.collect_all()

        assert "timestamp" in snapshot
        assert "cpu" in snapshot
        assert "memory" in snapshot
        assert "network" in snapshot
        assert "disk" in snapshot

        # All should have no errors
        assert snapshot["cpu"]["_error"] is None
        assert snapshot["memory"]["_error"] is None
        assert snapshot["network"]["_error"] is None
        assert snapshot["disk"]["_error"] is None
