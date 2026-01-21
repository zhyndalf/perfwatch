"""Tests for the memory bandwidth collector."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import time

from app.collectors.memory_bandwidth import MemoryBandwidthCollector, VMSTAT_PATH
from app.collectors.aggregator import MetricsAggregator


# Sample /proc/vmstat content
SAMPLE_VMSTAT = """nr_free_pages 1234567
nr_zone_inactive_anon 12345
nr_zone_active_anon 23456
pgpgin 1000000
pgpgout 500000
pswpin 100
pswpout 50
pgfault 5000000
pgmajfault 1000
"""

SAMPLE_VMSTAT_UPDATED = """nr_free_pages 1234567
nr_zone_inactive_anon 12345
nr_zone_active_anon 23456
pgpgin 1010000
pgpgout 505000
pswpin 110
pswpout 55
pgfault 5010000
pgmajfault 1010
"""


class TestMemoryBandwidthCollector:
    """Tests for MemoryBandwidthCollector class."""

    def test_collector_name(self):
        """Test that collector has correct name."""
        collector = MemoryBandwidthCollector()
        assert collector.name == "memory_bandwidth"

    def test_collector_repr(self):
        """Test collector string representation."""
        collector = MemoryBandwidthCollector()
        repr_str = repr(collector)
        assert "MemoryBandwidthCollector" in repr_str
        assert "memory_bandwidth" in repr_str

    def test_disabled_collector(self):
        """Test that disabled collector returns disabled status."""
        collector = MemoryBandwidthCollector(enabled=False)
        assert collector.enabled is False

    @pytest.mark.asyncio
    async def test_disabled_collector_safe_collect(self):
        """Test that disabled collector returns disabled status via safe_collect."""
        collector = MemoryBandwidthCollector(enabled=False)
        data = await collector.safe_collect()
        assert data["_enabled"] is False

    @pytest.mark.asyncio
    async def test_collect_returns_availability_field(self):
        """Test that collect() always returns an 'available' field."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                data = await collector.collect()

        assert "available" in data
        assert isinstance(data["available"], bool)


class TestMemoryBandwidthAvailability:
    """Tests for availability detection."""

    def test_is_available_returns_bool(self):
        """Test that is_available() returns a boolean."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                result = collector.is_available()

        assert isinstance(result, bool)
        assert result is True

    def test_is_available_caches_result(self):
        """Test that is_available() caches its result."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                result1 = collector.is_available()

        # Set cached value to test caching
        collector._available = False
        result2 = collector.is_available()

        assert result2 is False  # Should use cached value

    def test_unavailable_when_vmstat_missing(self):
        """Test availability when /proc/vmstat doesn't exist."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=False):
            result = collector.is_available()

        assert result is False


class TestMemoryBandwidthGracefulDegradation:
    """Tests for graceful handling of errors."""

    @pytest.mark.asyncio
    async def test_no_crash_on_missing_vmstat(self):
        """Test graceful handling when /proc/vmstat is missing."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=False):
            data = await collector.collect()

        assert data["available"] is False

    @pytest.mark.asyncio
    async def test_no_crash_on_read_error(self):
        """Test graceful handling when vmstat read fails."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', side_effect=IOError("Permission denied")):
                data = await collector.collect()

        assert data["available"] is False

    @pytest.mark.asyncio
    async def test_no_crash_on_malformed_vmstat(self):
        """Test graceful handling when vmstat content is malformed."""
        collector = MemoryBandwidthCollector()

        malformed_content = "this is not valid vmstat content\n"

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=malformed_content):
                data = await collector.collect()

        assert data["available"] is False


class TestMemoryBandwidthFirstCollection:
    """Tests for first collection (before rate can be calculated)."""

    @pytest.mark.asyncio
    async def test_first_collection_returns_zeros(self):
        """Test that first collection returns zeros for rate metrics."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                data = await collector.collect()

        assert data["available"] is True
        assert data["pgpgin_per_sec"] == 0.0
        assert data["pgpgout_per_sec"] == 0.0
        assert data["pswpin_per_sec"] == 0.0
        assert data["pswpout_per_sec"] == 0.0
        assert data["page_io_bytes_per_sec"] == 0.0
        assert data["swap_io_bytes_per_sec"] == 0.0
        assert data["pgfault_per_sec"] == 0.0
        assert data["pgmajfault_per_sec"] == 0.0


class TestMemoryBandwidthRateCalculation:
    """Tests for rate calculation over multiple collections."""

    @pytest.mark.asyncio
    async def test_rate_calculation(self):
        """Test rate calculation between two collections."""
        collector = MemoryBandwidthCollector()

        # First collection
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                with patch('app.utils.rate_calculator.time.time', return_value=0.0):
                    data1 = await collector.collect()

        assert data1["available"] is True
        assert data1["pgpgin_per_sec"] == 0.0  # First call returns zeros

        # Second collection (1 second later, with updated values)
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT_UPDATED):
                with patch('app.utils.rate_calculator.time.time', return_value=1.0):
                    data2 = await collector.collect()

        assert data2["available"] is True
        # pgpgin increased by 10000 KB in 1 second = 10000 KB/sec
        assert data2["pgpgin_per_sec"] == 10000.0
        # pgpgout increased by 5000 KB in 1 second = 5000 KB/sec
        assert data2["pgpgout_per_sec"] == 5000.0
        # pswpin increased by 10 pages in 1 second
        assert data2["pswpin_per_sec"] == 10.0
        # pswpout increased by 5 pages in 1 second
        assert data2["pswpout_per_sec"] == 5.0
        # page_io_bytes_per_sec = (10000 + 5000) * 1024
        assert data2["page_io_bytes_per_sec"] == 15360000.0
        # swap_io_bytes_per_sec = (10 + 5) * 4096
        assert data2["swap_io_bytes_per_sec"] == 61440.0
        # pgfault increased by 10000 in 1 second
        assert data2["pgfault_per_sec"] == 10000.0
        # pgmajfault increased by 10 in 1 second
        assert data2["pgmajfault_per_sec"] == 10.0

    @pytest.mark.asyncio
    async def test_rate_with_longer_interval(self):
        """Test rate calculation with 5 second interval."""
        collector = MemoryBandwidthCollector()

        # First collection
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                with patch('app.utils.rate_calculator.time.time', return_value=0.0):
                    await collector.collect()

        # Second collection (5 seconds later)
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT_UPDATED):
                with patch('app.utils.rate_calculator.time.time', return_value=5.0):
                    data = await collector.collect()

        # pgpgin increased by 10000 KB in 5 seconds = 2000 KB/sec
        assert data["pgpgin_per_sec"] == 2000.0
        # pgpgout increased by 5000 KB in 5 seconds = 1000 KB/sec
        assert data["pgpgout_per_sec"] == 1000.0


class TestMemoryBandwidthReset:
    """Tests for collector reset functionality."""

    def test_reset_clears_state(self):
        """Test that reset() clears cached state."""
        collector = MemoryBandwidthCollector()

        # Set some state in the rate calculator
        collector._rate_calculator._last_counters = {"pgpgin": 1000}
        collector._rate_calculator._last_times = {"pgpgin": 123.0}
        collector._available = True

        collector.reset()

        # Check that rate calculator state is cleared
        assert len(collector._rate_calculator._last_counters) == 0
        assert len(collector._rate_calculator._last_times) == 0
        assert collector._available is None


class TestMemoryBandwidthIntegration:
    """Integration tests with the aggregator."""

    @pytest.mark.asyncio
    async def test_with_aggregator(self):
        """Test memory bandwidth collector works with MetricsAggregator."""
        collector = MemoryBandwidthCollector()
        aggregator = MetricsAggregator(collectors=[collector])

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                snapshot = await aggregator.collect_all()

        assert "timestamp" in snapshot
        assert "memory_bandwidth" in snapshot
        assert snapshot["memory_bandwidth"]["_error"] is None
        assert "available" in snapshot["memory_bandwidth"]

    @pytest.mark.asyncio
    async def test_with_multiple_collectors(self):
        """Test memory bandwidth alongside other collectors in aggregator."""
        from app.collectors import CPUCollector, MemoryCollector

        aggregator = MetricsAggregator(
            collectors=[
                CPUCollector(),
                MemoryCollector(),
                MemoryBandwidthCollector(),
            ]
        )

        snapshot = await aggregator.collect_all()

        assert "cpu" in snapshot
        assert "memory" in snapshot
        assert "memory_bandwidth" in snapshot
        assert "available" in snapshot["memory_bandwidth"]


class TestMemoryBandwidthMetricsStructure:
    """Tests for metrics structure and field presence."""

    @pytest.mark.asyncio
    async def test_all_fields_present_when_available(self):
        """Test that all expected fields are present when metrics available."""
        collector = MemoryBandwidthCollector()

        # First collection to prime
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                with patch('time.monotonic', return_value=0.0):
                    await collector.collect()

        # Second collection to get rates
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT_UPDATED):
                with patch('time.monotonic', return_value=1.0):
                    data = await collector.collect()

        expected_fields = [
            "available",
            "pgpgin_per_sec",
            "pgpgout_per_sec",
            "pswpin_per_sec",
            "pswpout_per_sec",
            "page_io_bytes_per_sec",
            "swap_io_bytes_per_sec",
            "pgfault_per_sec",
            "pgmajfault_per_sec",
        ]

        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_values_are_numeric(self):
        """Test that metric values are numeric types."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                data = await collector.collect()

        assert isinstance(data["available"], bool)
        assert isinstance(data["pgpgin_per_sec"], float)
        assert isinstance(data["pgpgout_per_sec"], float)
        assert isinstance(data["page_io_bytes_per_sec"], float)


class TestMemoryBandwidthEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_handles_zero_time_delta(self):
        """Test handling when time delta is zero or very small."""
        collector = MemoryBandwidthCollector()

        # First collection
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                with patch('time.monotonic', return_value=100.0):
                    await collector.collect()

        # Second collection at same time (edge case)
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT_UPDATED):
                with patch('time.monotonic', return_value=100.0):
                    # Should not crash
                    data = await collector.collect()

        assert data["available"] is True
        # Values should be finite (using time_delta = 1.0 fallback)
        assert data["pgpgin_per_sec"] >= 0

    @pytest.mark.asyncio
    async def test_handles_missing_optional_metrics(self):
        """Test handling when some metrics are missing from vmstat."""
        collector = MemoryBandwidthCollector()

        # Minimal vmstat with only required fields
        minimal_vmstat = "pgpgin 1000\npgpgout 500\n"

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=minimal_vmstat):
                data = await collector.collect()

        assert data["available"] is True
        # Optional fields should use 0 as default
        assert data["pswpin_per_sec"] == 0.0
        assert data["pgfault_per_sec"] == 0.0


class TestVmstatParsing:
    """Tests for /proc/vmstat parsing logic."""

    def test_parse_vmstat_extracts_required_fields(self):
        """Test that _parse_vmstat extracts all required fields."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                values = collector._parse_vmstat()

        assert values is not None
        assert "pgpgin" in values
        assert "pgpgout" in values
        assert "pswpin" in values
        assert "pswpout" in values
        assert "pgfault" in values
        assert "pgmajfault" in values

        assert values["pgpgin"] == 1000000
        assert values["pgpgout"] == 500000
        assert values["pswpin"] == 100
        assert values["pswpout"] == 50

    def test_parse_vmstat_returns_none_on_missing_file(self):
        """Test that _parse_vmstat returns None when file missing."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=False):
            values = collector._parse_vmstat()

        assert values is None

    def test_parse_vmstat_handles_invalid_values(self):
        """Test that _parse_vmstat handles non-integer values."""
        collector = MemoryBandwidthCollector()

        invalid_vmstat = "pgpgin invalid\npgpgout 500\n"

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=invalid_vmstat):
                values = collector._parse_vmstat()

        # Should still work, just skip invalid entry
        # But since pgpgin is missing, should return None (required field)
        assert values is None


class TestMemoryBandwidthSafeCollect:
    """Tests for safe_collect wrapper functionality."""

    @pytest.mark.asyncio
    async def test_safe_collect_adds_metadata(self):
        """Test that safe_collect adds timestamp and error fields."""
        collector = MemoryBandwidthCollector()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=SAMPLE_VMSTAT):
                data = await collector.safe_collect()

        assert "_timestamp" in data
        assert "_error" in data
        assert data["_error"] is None
        # _enabled is only added when collector is disabled
        assert "available" in data
