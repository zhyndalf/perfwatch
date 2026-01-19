"""Tests for the collector infrastructure."""

import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.collectors.base import BaseCollector
from app.collectors.aggregator import MetricsAggregator


# === Test Collectors (Mock implementations) ===


class MockCPUCollector(BaseCollector):
    """Mock CPU collector for testing."""

    name = "cpu"

    async def collect(self) -> Dict[str, Any]:
        return {
            "usage_percent": 45.2,
            "per_core": [40.1, 50.3, 42.8, 47.6],
            "user": 30.5,
            "system": 14.7,
        }


class MockMemoryCollector(BaseCollector):
    """Mock Memory collector for testing."""

    name = "memory"

    async def collect(self) -> Dict[str, Any]:
        return {
            "total_bytes": 16_000_000_000,
            "available_bytes": 8_000_000_000,
            "used_bytes": 8_000_000_000,
            "usage_percent": 50.0,
        }


class FailingCollector(BaseCollector):
    """Collector that always fails, for testing error handling."""

    name = "failing"

    async def collect(self) -> Dict[str, Any]:
        raise RuntimeError("Simulated collection failure")


class SlowCollector(BaseCollector):
    """Collector with artificial delay, for testing concurrency."""

    name = "slow"

    def __init__(self, delay: float = 0.1):
        super().__init__()
        self.delay = delay

    async def collect(self) -> Dict[str, Any]:
        await asyncio.sleep(self.delay)
        return {"delayed": True, "delay_seconds": self.delay}


# === BaseCollector Tests ===


class TestBaseCollector:
    """Tests for BaseCollector abstract class."""

    @pytest.mark.asyncio
    async def test_collect_returns_data(self):
        """Test that collect() returns expected data."""
        collector = MockCPUCollector()
        data = await collector.collect()

        assert "usage_percent" in data
        assert data["usage_percent"] == 45.2
        assert len(data["per_core"]) == 4

    @pytest.mark.asyncio
    async def test_safe_collect_adds_timestamp(self):
        """Test that safe_collect() adds timestamp to data."""
        collector = MockCPUCollector()
        data = await collector.safe_collect()

        assert "_timestamp" in data
        assert "_error" in data
        assert data["_error"] is None

    @pytest.mark.asyncio
    async def test_safe_collect_handles_errors(self):
        """Test that safe_collect() catches exceptions gracefully."""
        collector = FailingCollector()
        data = await collector.safe_collect()

        assert "_error" in data
        assert "Simulated collection failure" in data["_error"]
        assert "_timestamp" in data

    @pytest.mark.asyncio
    async def test_disabled_collector(self):
        """Test that disabled collector returns disabled status."""
        collector = MockCPUCollector(enabled=False)
        data = await collector.safe_collect()

        assert data["_enabled"] is False
        assert "_timestamp" in data
        # Should not have actual metrics
        assert "usage_percent" not in data

    def test_collector_repr(self):
        """Test collector string representation."""
        collector = MockCPUCollector()
        repr_str = repr(collector)

        assert "MockCPUCollector" in repr_str
        assert "cpu" in repr_str
        assert "enabled=True" in repr_str


# === MetricsAggregator Tests ===


class TestMetricsAggregator:
    """Tests for MetricsAggregator class."""

    def test_init_empty(self):
        """Test creating aggregator with no collectors."""
        aggregator = MetricsAggregator()

        assert len(aggregator.collectors) == 0
        assert aggregator.interval == 5.0

    def test_init_with_collectors(self):
        """Test creating aggregator with collectors."""
        collectors = [MockCPUCollector(), MockMemoryCollector()]
        aggregator = MetricsAggregator(collectors=collectors, interval=10.0)

        assert len(aggregator.collectors) == 2
        assert aggregator.interval == 10.0

    def test_add_collector(self):
        """Test adding a collector."""
        aggregator = MetricsAggregator()
        aggregator.add_collector(MockCPUCollector())

        assert len(aggregator.collectors) == 1
        assert aggregator.collector_names == ["cpu"]

    def test_remove_collector(self):
        """Test removing a collector by name."""
        aggregator = MetricsAggregator(collectors=[MockCPUCollector(), MockMemoryCollector()])

        result = aggregator.remove_collector("cpu")

        assert result is True
        assert len(aggregator.collectors) == 1
        assert aggregator.collector_names == ["memory"]

    def test_remove_nonexistent_collector(self):
        """Test removing a collector that doesn't exist."""
        aggregator = MetricsAggregator()

        result = aggregator.remove_collector("nonexistent")

        assert result is False

    def test_get_collector(self):
        """Test getting a collector by name."""
        cpu_collector = MockCPUCollector()
        aggregator = MetricsAggregator(collectors=[cpu_collector])

        found = aggregator.get_collector("cpu")

        assert found is cpu_collector

    def test_get_nonexistent_collector(self):
        """Test getting a collector that doesn't exist."""
        aggregator = MetricsAggregator()

        found = aggregator.get_collector("nonexistent")

        assert found is None

    @pytest.mark.asyncio
    async def test_collect_all(self):
        """Test collecting from all collectors."""
        aggregator = MetricsAggregator(
            collectors=[MockCPUCollector(), MockMemoryCollector()]
        )

        snapshot = await aggregator.collect_all()

        assert "timestamp" in snapshot
        assert "cpu" in snapshot
        assert "memory" in snapshot
        assert snapshot["cpu"]["usage_percent"] == 45.2
        assert snapshot["memory"]["usage_percent"] == 50.0

    @pytest.mark.asyncio
    async def test_collect_all_with_failing_collector(self):
        """Test that one failing collector doesn't break others."""
        aggregator = MetricsAggregator(
            collectors=[MockCPUCollector(), FailingCollector(), MockMemoryCollector()]
        )

        snapshot = await aggregator.collect_all()

        # CPU and Memory should still have data
        assert snapshot["cpu"]["usage_percent"] == 45.2
        assert snapshot["memory"]["usage_percent"] == 50.0
        # Failing collector should have error
        assert snapshot["failing"]["_error"] is not None

    @pytest.mark.asyncio
    async def test_collect_all_concurrent(self):
        """Test that collectors run concurrently."""
        # Create 3 slow collectors, each taking 0.1s
        aggregator = MetricsAggregator(
            collectors=[SlowCollector(0.1), SlowCollector(0.1), SlowCollector(0.1)]
        )

        import time
        start = time.time()
        await aggregator.collect_all()
        elapsed = time.time() - start

        # If running sequentially, would take ~0.3s
        # If concurrent, should take ~0.1s (plus overhead)
        assert elapsed < 0.25, f"Collection took {elapsed}s, expected concurrent execution"

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        """Test starting and stopping periodic collection."""
        aggregator = MetricsAggregator(
            collectors=[MockCPUCollector()],
            interval=0.05,  # 50ms for faster testing
        )

        collected_snapshots = []

        async def callback(snapshot):
            collected_snapshots.append(snapshot)
            if len(collected_snapshots) >= 3:
                aggregator.stop()

        # Start collection in background
        task = asyncio.create_task(aggregator.start(callback))

        # Wait for collection to complete
        await asyncio.wait_for(task, timeout=1.0)

        assert len(collected_snapshots) >= 3
        assert not aggregator.is_running

    @pytest.mark.asyncio
    async def test_start_with_sync_callback(self):
        """Test that sync callbacks work too."""
        aggregator = MetricsAggregator(
            collectors=[MockCPUCollector()],
            interval=0.05,
        )

        collected = []

        def sync_callback(snapshot):
            collected.append(snapshot)
            if len(collected) >= 2:
                aggregator.stop()

        task = asyncio.create_task(aggregator.start(sync_callback))
        await asyncio.wait_for(task, timeout=1.0)

        assert len(collected) >= 2

    def test_is_running_property(self):
        """Test is_running property."""
        aggregator = MetricsAggregator()

        assert aggregator.is_running is False

    def test_collector_names_property(self):
        """Test collector_names property."""
        aggregator = MetricsAggregator(
            collectors=[MockCPUCollector(), MockMemoryCollector()]
        )

        names = aggregator.collector_names

        assert names == ["cpu", "memory"]

    def test_aggregator_repr(self):
        """Test aggregator string representation."""
        aggregator = MetricsAggregator(
            collectors=[MockCPUCollector()],
            interval=5.0,
        )

        repr_str = repr(aggregator)

        assert "MetricsAggregator" in repr_str
        assert "cpu" in repr_str
        assert "5.0" in repr_str


# === Integration-like Tests ===


class TestCollectorIntegration:
    """Integration-style tests for the collector system."""

    @pytest.mark.asyncio
    async def test_full_collection_cycle(self):
        """Test a complete collection cycle with multiple collectors."""
        # Setup
        cpu = MockCPUCollector()
        memory = MockMemoryCollector()
        aggregator = MetricsAggregator(collectors=[cpu, memory])

        # Collect
        snapshot = await aggregator.collect_all()

        # Verify structure
        assert "timestamp" in snapshot
        assert "cpu" in snapshot
        assert "memory" in snapshot

        # Verify CPU data
        cpu_data = snapshot["cpu"]
        assert cpu_data["usage_percent"] == 45.2
        assert cpu_data["_error"] is None
        assert "_timestamp" in cpu_data

        # Verify Memory data
        mem_data = snapshot["memory"]
        assert mem_data["total_bytes"] == 16_000_000_000
        assert mem_data["_error"] is None

    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test that system continues working when some collectors fail."""
        # Mix of working and failing collectors
        aggregator = MetricsAggregator(
            collectors=[
                MockCPUCollector(),
                FailingCollector(),
                MockMemoryCollector(),
            ]
        )

        # Should not raise, should return partial data
        snapshot = await aggregator.collect_all()

        # Working collectors have data
        assert snapshot["cpu"]["_error"] is None
        assert snapshot["memory"]["_error"] is None

        # Failing collector has error info but didn't crash
        assert snapshot["failing"]["_error"] is not None
        assert "_timestamp" in snapshot["failing"]
