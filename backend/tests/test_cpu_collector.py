"""Tests for the CPU collector."""

import pytest
from unittest.mock import patch, MagicMock

from app.collectors.cpu import CPUCollector
from app.collectors.aggregator import MetricsAggregator


class TestCPUCollector:
    """Tests for CPUCollector class."""

    @pytest.mark.asyncio
    async def test_collect_returns_usage_percent(self):
        """Test that collect() returns overall CPU usage."""
        collector = CPUCollector()
        data = await collector.collect()

        assert "usage_percent" in data
        assert isinstance(data["usage_percent"], (int, float))
        assert 0 <= data["usage_percent"] <= 100

    @pytest.mark.asyncio
    async def test_collect_returns_per_core(self):
        """Test that collect() returns per-core usage."""
        collector = CPUCollector()
        data = await collector.collect()

        assert "per_core" in data
        assert isinstance(data["per_core"], list)
        assert len(data["per_core"]) > 0
        for core_usage in data["per_core"]:
            assert 0 <= core_usage <= 100

    @pytest.mark.asyncio
    async def test_collect_returns_time_breakdown(self):
        """Test that collect() returns user/system/idle times."""
        collector = CPUCollector()
        data = await collector.collect()

        assert "user" in data
        assert "system" in data
        assert "idle" in data
        assert isinstance(data["user"], (int, float))
        assert isinstance(data["system"], (int, float))
        assert isinstance(data["idle"], (int, float))

    @pytest.mark.asyncio
    async def test_collect_returns_core_count(self):
        """Test that collect() returns core counts."""
        collector = CPUCollector()
        data = await collector.collect()

        assert "core_count" in data
        assert "physical_cores" in data
        assert data["core_count"] > 0
        assert data["physical_cores"] is None or data["physical_cores"] > 0

    @pytest.mark.asyncio
    async def test_collect_handles_optional_fields(self):
        """Test that optional fields are present (may be None)."""
        collector = CPUCollector()
        data = await collector.collect()

        # These fields should exist but may be None on some systems
        assert "iowait" in data
        assert "frequency_mhz" in data
        assert "load_avg" in data
        assert "temperature" in data

    @pytest.mark.asyncio
    async def test_collect_load_avg_format(self):
        """Test load average format when available."""
        collector = CPUCollector()
        data = await collector.collect()

        if data["load_avg"] is not None:
            assert isinstance(data["load_avg"], list)
            assert len(data["load_avg"]) == 3  # 1, 5, 15 min
            for load in data["load_avg"]:
                assert isinstance(load, (int, float))
                assert load >= 0

    @pytest.mark.asyncio
    async def test_collect_frequency_format(self):
        """Test frequency format when available."""
        collector = CPUCollector()
        data = await collector.collect()

        if data["frequency_mhz"] is not None:
            assert isinstance(data["frequency_mhz"], list)
            assert len(data["frequency_mhz"]) >= 1
            for freq in data["frequency_mhz"]:
                assert isinstance(freq, (int, float))
                assert freq >= 0

    @pytest.mark.asyncio
    async def test_safe_collect_adds_metadata(self):
        """Test that safe_collect adds timestamp and error fields."""
        collector = CPUCollector()
        data = await collector.safe_collect()

        assert "_timestamp" in data
        assert "_error" in data
        assert data["_error"] is None

    @pytest.mark.asyncio
    async def test_disabled_collector(self):
        """Test that disabled collector returns disabled status."""
        collector = CPUCollector(enabled=False)
        data = await collector.safe_collect()

        assert data["_enabled"] is False
        assert "usage_percent" not in data

    def test_collector_name(self):
        """Test that collector has correct name."""
        collector = CPUCollector()
        assert collector.name == "cpu"

    def test_collector_repr(self):
        """Test collector string representation."""
        collector = CPUCollector()
        repr_str = repr(collector)

        assert "CPUCollector" in repr_str
        assert "cpu" in repr_str


class TestCPUCollectorGracefulDegradation:
    """Tests for graceful handling of unavailable metrics."""

    @pytest.mark.asyncio
    async def test_frequency_unavailable(self):
        """Test handling when frequency is unavailable."""
        collector = CPUCollector()

        with patch.object(collector, "_get_frequency", return_value=None):
            data = await collector.collect()

        assert data["frequency_mhz"] is None
        # Other metrics should still work
        assert "usage_percent" in data

    @pytest.mark.asyncio
    async def test_temperature_unavailable(self):
        """Test handling when temperature is unavailable."""
        collector = CPUCollector()

        with patch.object(collector, "_get_temperature", return_value=None):
            data = await collector.collect()

        assert data["temperature"] is None
        assert "usage_percent" in data

    @pytest.mark.asyncio
    async def test_load_avg_unavailable(self):
        """Test handling when load average is unavailable."""
        collector = CPUCollector()

        with patch.object(collector, "_get_load_average", return_value=None):
            data = await collector.collect()

        assert data["load_avg"] is None
        assert "usage_percent" in data


class TestCPUCollectorIntegration:
    """Integration tests with the aggregator."""

    @pytest.mark.asyncio
    async def test_with_aggregator(self):
        """Test CPU collector works with MetricsAggregator."""
        cpu_collector = CPUCollector()
        aggregator = MetricsAggregator(collectors=[cpu_collector])

        snapshot = await aggregator.collect_all()

        assert "timestamp" in snapshot
        assert "cpu" in snapshot
        assert snapshot["cpu"]["_error"] is None
        assert "usage_percent" in snapshot["cpu"]

    @pytest.mark.asyncio
    async def test_multiple_collections(self):
        """Test multiple consecutive collections work correctly."""
        collector = CPUCollector()

        # Collect multiple times
        results = []
        for _ in range(3):
            data = await collector.collect()
            results.append(data)

        # All should have valid data
        for result in results:
            assert "usage_percent" in result
            assert "per_core" in result
            assert isinstance(result["usage_percent"], (int, float))
