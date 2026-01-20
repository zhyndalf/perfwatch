"""Tests for the perf_events collector."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import os

from app.collectors.perf_events import (
    PerfEventsCollector,
    PerfEventAttr,
    PERF_TYPE_HARDWARE,
    PERF_TYPE_HW_CACHE,
    PERF_COUNT_HW_CPU_CYCLES,
    PERF_COUNT_HW_INSTRUCTIONS,
    PERF_COUNT_HW_CACHE_L1D,
    PERF_COUNT_HW_CACHE_LL,
    PERF_COUNT_HW_CACHE_BPU,
    PERF_COUNT_HW_CACHE_DTLB,
    PERF_COUNT_HW_CACHE_OP_READ,
    PERF_COUNT_HW_CACHE_RESULT_ACCESS,
    PERF_COUNT_HW_CACHE_RESULT_MISS,
    CACHE_L1D_READ_ACCESS,
    CACHE_L1D_READ_MISS,
    CACHE_LL_READ_ACCESS,
    CACHE_LL_READ_MISS,
    CACHE_BPU_READ_ACCESS,
    CACHE_BPU_READ_MISS,
    CACHE_DTLB_READ_ACCESS,
    CACHE_DTLB_READ_MISS,
    encode_cache_config,
    _get_arch,
)
from app.collectors.aggregator import MetricsAggregator


class TestPerfEventsCollector:
    """Tests for PerfEventsCollector class."""

    def test_collector_name(self):
        """Test that collector has correct name."""
        collector = PerfEventsCollector()
        assert collector.name == "perf_events"

    def test_collector_repr(self):
        """Test collector string representation."""
        collector = PerfEventsCollector()
        repr_str = repr(collector)

        assert "PerfEventsCollector" in repr_str
        assert "perf_events" in repr_str

    def test_disabled_collector(self):
        """Test that disabled collector returns disabled status."""
        collector = PerfEventsCollector(enabled=False)
        # Force initialization bypass by checking _available
        assert collector.enabled is False

    @pytest.mark.asyncio
    async def test_disabled_collector_safe_collect(self):
        """Test that disabled collector returns disabled status via safe_collect."""
        collector = PerfEventsCollector(enabled=False)
        data = await collector.safe_collect()

        assert data["_enabled"] is False
        assert "available" not in data

    @pytest.mark.asyncio
    async def test_collect_returns_availability_field(self):
        """Test that collect() always returns an 'available' field."""
        collector = PerfEventsCollector()
        data = await collector.collect()

        assert "available" in data
        assert isinstance(data["available"], bool)

    @pytest.mark.asyncio
    async def test_collect_when_unavailable_returns_false(self):
        """Test that collect returns available=False when perf_events unavailable."""
        collector = PerfEventsCollector()

        # Mock the paranoid check to return False
        with patch.object(collector, "_check_paranoid", return_value=False):
            collector._initialized = False  # Reset to force re-initialization
            collector._available = None
            data = await collector.collect()

        assert data["available"] is False

    @pytest.mark.asyncio
    async def test_collect_graceful_on_missing_paranoid_file(self):
        """Test graceful handling when /proc/sys/kernel/perf_event_paranoid is missing."""
        collector = PerfEventsCollector()

        with patch("os.path.exists", return_value=False):
            collector._initialized = False
            collector._available = None
            data = await collector.collect()

        assert data["available"] is False

    @pytest.mark.asyncio
    async def test_safe_collect_adds_metadata(self):
        """Test that safe_collect adds timestamp and error fields."""
        collector = PerfEventsCollector()
        data = await collector.safe_collect()

        assert "_timestamp" in data
        assert "_error" in data
        assert data["_error"] is None


class TestPerfEventsAvailability:
    """Tests for availability detection."""

    def test_is_available_returns_bool(self):
        """Test that is_available() returns a boolean."""
        collector = PerfEventsCollector()
        result = collector.is_available()

        assert isinstance(result, bool)

    def test_is_available_caches_result(self):
        """Test that is_available() caches its result."""
        collector = PerfEventsCollector()

        # First call
        result1 = collector.is_available()
        # Set a flag to verify we're using cached value
        collector._available = True

        result2 = collector.is_available()

        assert result2 is True  # Should use cached value

    def test_check_paranoid_with_valid_file(self):
        """Test _check_paranoid with a valid paranoid file."""
        collector = PerfEventsCollector()

        mock_content = "2\n"
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_content)):
                result = collector._check_paranoid()

        assert result is True

    def test_check_paranoid_with_missing_file(self):
        """Test _check_paranoid when paranoid file doesn't exist."""
        collector = PerfEventsCollector()

        with patch("os.path.exists", return_value=False):
            result = collector._check_paranoid()

        assert result is False


class TestPerfEventsGracefulDegradation:
    """Tests for graceful handling of errors and unavailable resources."""

    @pytest.mark.asyncio
    async def test_no_crash_on_permission_denied(self):
        """Test that collector doesn't crash on permission errors."""
        collector = PerfEventsCollector()

        # Simulate permission denied on syscall
        with patch.object(collector, "_perf_event_open", return_value=-1):
            collector._initialized = False
            collector._available = None
            data = await collector.collect()

        # Should return unavailable, not crash
        assert data["available"] is False

    @pytest.mark.asyncio
    async def test_no_crash_on_syscall_not_found(self):
        """Test graceful handling when syscall number not found for architecture."""
        collector = PerfEventsCollector()

        with patch("app.collectors.perf_events._get_arch", return_value="unknown_arch"):
            collector._initialized = False
            collector._available = None
            data = await collector.collect()

        assert data["available"] is False

    @pytest.mark.asyncio
    async def test_no_crash_on_libc_error(self):
        """Test graceful handling when libc loading fails."""
        collector = PerfEventsCollector()

        with patch("app.collectors.perf_events._get_libc", side_effect=OSError("libc not found")):
            collector._initialized = False
            collector._available = None
            data = await collector.collect()

        assert data["available"] is False

    @pytest.mark.asyncio
    async def test_collect_with_partial_events(self):
        """Test collection when only some events are available."""
        collector = PerfEventsCollector()

        # Simulate only cycles available, not instructions
        collector._available = True
        collector._initialized = True
        collector._fds = {"cycles": 10}  # Only cycles

        try:
            with patch.object(collector, "_read_counter", return_value=1000):
                data = await collector.collect()

            assert data["available"] is True
            assert data["cycles"] == 1000
            assert data["instructions"] is None
            assert data["ipc"] is None  # Can't calculate without instructions
        finally:
            # Clear FDs to prevent close() on fake FDs during cleanup
            collector._fds = {}


class TestPerfEventsMetricsCalculation:
    """Tests for metrics calculation."""

    @pytest.mark.asyncio
    async def test_ipc_calculation(self):
        """Test IPC (Instructions Per Cycle) calculation."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {"cycles": 10, "instructions": 11}

        def mock_read(fd):
            if fd == 10:  # cycles
                return 1000
            elif fd == 11:  # instructions
                return 1500
            return None

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            assert data["cycles"] == 1000
            assert data["instructions"] == 1500
            assert data["ipc"] == 1.5  # 1500 / 1000
        finally:
            # Clear FDs to prevent close() on fake FDs during cleanup
            collector._fds = {}

    @pytest.mark.asyncio
    async def test_ipc_zero_cycles(self):
        """Test IPC calculation when cycles is zero (avoid division by zero)."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {"cycles": 10, "instructions": 11}

        def mock_read(fd):
            if fd == 10:  # cycles
                return 0
            elif fd == 11:  # instructions
                return 100
            return None

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            assert data["cycles"] == 0
            assert data["instructions"] == 100
            assert data["ipc"] is None  # Should be None, not divide by zero
        finally:
            # Clear FDs to prevent close() on fake FDs during cleanup
            collector._fds = {}


class TestPerfEventsIntegration:
    """Integration tests with the aggregator."""

    @pytest.mark.asyncio
    async def test_with_aggregator(self):
        """Test perf_events collector works with MetricsAggregator."""
        perf_collector = PerfEventsCollector()
        aggregator = MetricsAggregator(collectors=[perf_collector])

        snapshot = await aggregator.collect_all()

        assert "timestamp" in snapshot
        assert "perf_events" in snapshot
        # Should have either data or error, but always available field
        assert snapshot["perf_events"]["_error"] is None
        assert "available" in snapshot["perf_events"]

    @pytest.mark.asyncio
    async def test_with_multiple_collectors(self):
        """Test perf_events alongside other collectors in aggregator."""
        from app.collectors import CPUCollector, MemoryCollector

        aggregator = MetricsAggregator(
            collectors=[
                CPUCollector(),
                MemoryCollector(),
                PerfEventsCollector(),
            ]
        )

        snapshot = await aggregator.collect_all()

        assert "cpu" in snapshot
        assert "memory" in snapshot
        assert "perf_events" in snapshot
        assert "available" in snapshot["perf_events"]


class TestPerfEventAttrStructure:
    """Tests for the perf_event_attr structure."""

    def test_structure_size(self):
        """Test that the structure has reasonable size."""
        import ctypes
        size = ctypes.sizeof(PerfEventAttr)
        # The structure should be at least 88 bytes for basic operations
        # (type + size + config + sample_period + sample_type + read_format + flags + padding)
        assert size >= 88

    def test_structure_fields(self):
        """Test that required fields exist."""
        attr = PerfEventAttr()
        attr.type = PERF_TYPE_HARDWARE
        attr.config = PERF_COUNT_HW_CPU_CYCLES

        assert attr.type == PERF_TYPE_HARDWARE
        assert attr.config == PERF_COUNT_HW_CPU_CYCLES


class TestArchitectureDetection:
    """Tests for architecture detection."""

    def test_get_arch_returns_string(self):
        """Test that _get_arch returns a string."""
        arch = _get_arch()
        assert isinstance(arch, str)
        assert len(arch) > 0

    def test_get_arch_known_platforms(self):
        """Test architecture detection for known platforms."""
        with patch("platform.machine", return_value="x86_64"):
            assert _get_arch() == "x86_64"

        with patch("platform.machine", return_value="AMD64"):
            assert _get_arch() == "x86_64"

        with patch("platform.machine", return_value="aarch64"):
            assert _get_arch() == "aarch64"

        with patch("platform.machine", return_value="arm64"):
            assert _get_arch() == "aarch64"

        with patch("platform.machine", return_value="armv7l"):
            assert _get_arch() == "arm"


class TestPerfEventsCleanup:
    """Tests for resource cleanup."""

    def test_close_clears_fds(self):
        """Test that close() clears file descriptors."""
        collector = PerfEventsCollector()
        collector._fds = {"cycles": 10, "instructions": 11}
        collector._available = True
        collector._initialized = True

        with patch("os.close"):
            collector.close()

        assert collector._fds == {}
        assert collector._available is None
        assert collector._initialized is False

    def test_close_handles_errors(self):
        """Test that close() handles errors gracefully."""
        collector = PerfEventsCollector()
        collector._fds = {"cycles": 10}

        with patch("os.close", side_effect=OSError("close failed")):
            # Should not raise
            collector.close()

        assert collector._fds == {}


class TestCacheEventEncoding:
    """Tests for cache event configuration encoding."""

    def test_encode_cache_config_l1d_read_access(self):
        """Test encoding for L1D read access events."""
        config = encode_cache_config(
            PERF_COUNT_HW_CACHE_L1D,
            PERF_COUNT_HW_CACHE_OP_READ,
            PERF_COUNT_HW_CACHE_RESULT_ACCESS
        )
        # L1D=0, OP_READ=0, RESULT_ACCESS=0 => 0 | (0 << 8) | (0 << 16) = 0
        assert config == 0
        assert config == CACHE_L1D_READ_ACCESS

    def test_encode_cache_config_l1d_read_miss(self):
        """Test encoding for L1D read miss events."""
        config = encode_cache_config(
            PERF_COUNT_HW_CACHE_L1D,
            PERF_COUNT_HW_CACHE_OP_READ,
            PERF_COUNT_HW_CACHE_RESULT_MISS
        )
        # L1D=0, OP_READ=0, RESULT_MISS=1 => 0 | (0 << 8) | (1 << 16) = 65536
        assert config == 0x10000
        assert config == CACHE_L1D_READ_MISS

    def test_encode_cache_config_llc_read_access(self):
        """Test encoding for LLC read access events."""
        config = encode_cache_config(
            PERF_COUNT_HW_CACHE_LL,
            PERF_COUNT_HW_CACHE_OP_READ,
            PERF_COUNT_HW_CACHE_RESULT_ACCESS
        )
        # LL=2, OP_READ=0, RESULT_ACCESS=0 => 2 | (0 << 8) | (0 << 16) = 2
        assert config == 2
        assert config == CACHE_LL_READ_ACCESS

    def test_encode_cache_config_llc_read_miss(self):
        """Test encoding for LLC read miss events."""
        config = encode_cache_config(
            PERF_COUNT_HW_CACHE_LL,
            PERF_COUNT_HW_CACHE_OP_READ,
            PERF_COUNT_HW_CACHE_RESULT_MISS
        )
        # LL=2, OP_READ=0, RESULT_MISS=1 => 2 | (0 << 8) | (1 << 16) = 65538
        assert config == 0x10002
        assert config == CACHE_LL_READ_MISS


class TestCacheMetricsCollection:
    """Tests for cache metrics collection."""

    @pytest.mark.asyncio
    async def test_collect_cache_metrics_available(self):
        """Test full cache metrics collection when available."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "cycles": 10,
            "instructions": 11,
            "l1d_references": 12,
            "l1d_misses": 13,
            "llc_references": 14,
            "llc_misses": 15,
        }

        def mock_read(fd):
            values = {
                10: 1000000,    # cycles
                11: 800000,     # instructions
                12: 500000,     # l1d_references
                13: 5000,       # l1d_misses (1% miss rate)
                14: 100000,     # llc_references
                15: 10000,      # llc_misses (10% miss rate)
            }
            return values.get(fd)

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            # CPU counters
            assert data["cycles"] == 1000000
            assert data["instructions"] == 800000
            assert data["ipc"] == 0.8
            # L1D cache
            assert data["l1d_references"] == 500000
            assert data["l1d_misses"] == 5000
            assert data["l1d_miss_rate"] == pytest.approx(0.01)
            # LLC
            assert data["llc_references"] == 100000
            assert data["llc_misses"] == 10000
            assert data["llc_miss_rate"] == pytest.approx(0.1)
        finally:
            collector._fds = {}

    @pytest.mark.asyncio
    async def test_collect_cache_metrics_partial(self):
        """Test cache metrics when only some counters available."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        # Only L1D available, not LLC
        collector._fds = {
            "l1d_references": 12,
            "l1d_misses": 13,
        }

        def mock_read(fd):
            values = {
                12: 100000,     # l1d_references
                13: 2000,       # l1d_misses
            }
            return values.get(fd)

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            # L1D available
            assert data["l1d_references"] == 100000
            assert data["l1d_misses"] == 2000
            assert data["l1d_miss_rate"] == pytest.approx(0.02)
            # LLC not available
            assert data["llc_references"] is None
            assert data["llc_misses"] is None
            assert data["llc_miss_rate"] is None
        finally:
            collector._fds = {}

    @pytest.mark.asyncio
    async def test_cache_miss_rate_zero_references(self):
        """Test cache miss rate when references is zero (avoid division by zero)."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "l1d_references": 12,
            "l1d_misses": 13,
            "llc_references": 14,
            "llc_misses": 15,
        }

        def mock_read(fd):
            values = {
                12: 0,      # l1d_references (zero!)
                13: 0,      # l1d_misses
                14: 0,      # llc_references (zero!)
                15: 0,      # llc_misses
            }
            return values.get(fd)

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            # Miss rates should be None when references is zero
            assert data["l1d_miss_rate"] is None
            assert data["llc_miss_rate"] is None
        finally:
            collector._fds = {}

    @pytest.mark.asyncio
    async def test_cache_miss_rate_calculation(self):
        """Test cache miss rate calculation accuracy."""
        # Test various miss rates
        test_cases = [
            (1000000, 50000, 0.05),   # 5% miss rate
            (1000000, 100000, 0.1),   # 10% miss rate
            (1000000, 1000, 0.001),   # 0.1% miss rate
            (100, 100, 1.0),           # 100% miss rate
        ]

        for refs, misses, expected_rate in test_cases:
            collector = PerfEventsCollector()
            collector._available = True
            collector._initialized = True
            collector._fds = {
                "l1d_references": 12,
                "l1d_misses": 13,
            }

            def mock_read(fd, r=refs, m=misses):
                values = {12: r, 13: m}
                return values.get(fd)

            try:
                with patch.object(collector, "_read_counter", side_effect=mock_read):
                    data = await collector.collect()

                assert data["l1d_miss_rate"] == pytest.approx(expected_rate), \
                    f"Expected {expected_rate} for {misses}/{refs}"
            finally:
                collector._fds = {}


class TestCacheMetricsIntegration:
    """Integration tests for cache metrics."""

    @pytest.mark.asyncio
    async def test_cache_metrics_in_aggregator(self):
        """Test that cache metrics appear in aggregator output."""
        perf_collector = PerfEventsCollector()
        aggregator = MetricsAggregator(collectors=[perf_collector])

        snapshot = await aggregator.collect_all()

        assert "perf_events" in snapshot
        perf_data = snapshot["perf_events"]
        assert "available" in perf_data
        # Cache fields should exist (may be None if unavailable)
        if perf_data["available"]:
            assert "l1d_references" in perf_data
            assert "l1d_misses" in perf_data
            assert "l1d_miss_rate" in perf_data
            assert "llc_references" in perf_data
            assert "llc_misses" in perf_data
            assert "llc_miss_rate" in perf_data


class TestBranchPredictionEventEncoding:
    """Tests for branch prediction (BPU) event configuration encoding."""

    def test_encode_bpu_read_access(self):
        """Test encoding for BPU read access events."""
        config = encode_cache_config(
            PERF_COUNT_HW_CACHE_BPU,
            PERF_COUNT_HW_CACHE_OP_READ,
            PERF_COUNT_HW_CACHE_RESULT_ACCESS
        )
        # BPU=5, OP_READ=0, RESULT_ACCESS=0 => 5 | (0 << 8) | (0 << 16) = 5
        assert config == 5
        assert config == CACHE_BPU_READ_ACCESS

    def test_encode_bpu_read_miss(self):
        """Test encoding for BPU read miss events (mispredictions)."""
        config = encode_cache_config(
            PERF_COUNT_HW_CACHE_BPU,
            PERF_COUNT_HW_CACHE_OP_READ,
            PERF_COUNT_HW_CACHE_RESULT_MISS
        )
        # BPU=5, OP_READ=0, RESULT_MISS=1 => 5 | (0 << 8) | (1 << 16) = 65541
        assert config == 0x10005
        assert config == CACHE_BPU_READ_MISS


class TestDTLBEventEncoding:
    """Tests for Data TLB event configuration encoding."""

    def test_encode_dtlb_read_access(self):
        """Test encoding for DTLB read access events."""
        config = encode_cache_config(
            PERF_COUNT_HW_CACHE_DTLB,
            PERF_COUNT_HW_CACHE_OP_READ,
            PERF_COUNT_HW_CACHE_RESULT_ACCESS
        )
        # DTLB=3, OP_READ=0, RESULT_ACCESS=0 => 3 | (0 << 8) | (0 << 16) = 3
        assert config == 3
        assert config == CACHE_DTLB_READ_ACCESS

    def test_encode_dtlb_read_miss(self):
        """Test encoding for DTLB read miss events."""
        config = encode_cache_config(
            PERF_COUNT_HW_CACHE_DTLB,
            PERF_COUNT_HW_CACHE_OP_READ,
            PERF_COUNT_HW_CACHE_RESULT_MISS
        )
        # DTLB=3, OP_READ=0, RESULT_MISS=1 => 3 | (0 << 8) | (1 << 16) = 65539
        assert config == 0x10003
        assert config == CACHE_DTLB_READ_MISS


class TestBranchPredictionMetricsCollection:
    """Tests for branch prediction metrics collection."""

    @pytest.mark.asyncio
    async def test_collect_branch_metrics_available(self):
        """Test branch prediction metrics collection when available."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "branch_references": 20,
            "branch_misses": 21,
        }

        def mock_read(fd):
            values = {
                20: 1000000,    # branch_references
                21: 50000,      # branch_misses (5% miss rate)
            }
            return values.get(fd)

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            assert data["branch_references"] == 1000000
            assert data["branch_misses"] == 50000
            assert data["branch_miss_rate"] == pytest.approx(0.05)
        finally:
            collector._fds = {}

    @pytest.mark.asyncio
    async def test_collect_branch_metrics_partial(self):
        """Test branch metrics when only references available."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "branch_references": 20,
            # No branch_misses
        }

        def mock_read(fd):
            values = {20: 500000}
            return values.get(fd)

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            assert data["branch_references"] == 500000
            assert data["branch_misses"] is None
            assert data["branch_miss_rate"] is None
        finally:
            collector._fds = {}

    @pytest.mark.asyncio
    async def test_branch_miss_rate_zero_references(self):
        """Test branch miss rate when references is zero."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "branch_references": 20,
            "branch_misses": 21,
        }

        def mock_read(fd):
            return 0  # Both references and misses are zero

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            assert data["branch_miss_rate"] is None  # Avoid division by zero
        finally:
            collector._fds = {}


class TestDTLBMetricsCollection:
    """Tests for Data TLB metrics collection."""

    @pytest.mark.asyncio
    async def test_collect_dtlb_metrics_available(self):
        """Test DTLB metrics collection when available."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "dtlb_references": 22,
            "dtlb_misses": 23,
        }

        def mock_read(fd):
            values = {
                22: 2000000,    # dtlb_references
                23: 10000,      # dtlb_misses (0.5% miss rate)
            }
            return values.get(fd)

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            assert data["dtlb_references"] == 2000000
            assert data["dtlb_misses"] == 10000
            assert data["dtlb_miss_rate"] == pytest.approx(0.005)
        finally:
            collector._fds = {}

    @pytest.mark.asyncio
    async def test_collect_dtlb_metrics_partial(self):
        """Test DTLB metrics when only references available."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "dtlb_references": 22,
            # No dtlb_misses
        }

        def mock_read(fd):
            values = {22: 1000000}
            return values.get(fd)

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            assert data["dtlb_references"] == 1000000
            assert data["dtlb_misses"] is None
            assert data["dtlb_miss_rate"] is None
        finally:
            collector._fds = {}

    @pytest.mark.asyncio
    async def test_dtlb_miss_rate_zero_references(self):
        """Test DTLB miss rate when references is zero."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "dtlb_references": 22,
            "dtlb_misses": 23,
        }

        def mock_read(fd):
            return 0  # Both references and misses are zero

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            assert data["dtlb_miss_rate"] is None  # Avoid division by zero
        finally:
            collector._fds = {}


class TestAllCPUPerfMetricsCollection:
    """Tests for full CPU performance metrics collection."""

    @pytest.mark.asyncio
    async def test_collect_all_perf_metrics(self):
        """Test full collection of all CPU performance metrics."""
        collector = PerfEventsCollector()
        collector._available = True
        collector._initialized = True
        collector._fds = {
            "cycles": 10,
            "instructions": 11,
            "l1d_references": 12,
            "l1d_misses": 13,
            "llc_references": 14,
            "llc_misses": 15,
            "branch_references": 16,
            "branch_misses": 17,
            "dtlb_references": 18,
            "dtlb_misses": 19,
        }

        def mock_read(fd):
            values = {
                10: 10000000,   # cycles
                11: 8000000,    # instructions (0.8 IPC)
                12: 5000000,    # l1d_references
                13: 50000,      # l1d_misses (1% miss rate)
                14: 1000000,    # llc_references
                15: 100000,     # llc_misses (10% miss rate)
                16: 2000000,    # branch_references
                17: 40000,      # branch_misses (2% miss rate)
                18: 3000000,    # dtlb_references
                19: 3000,       # dtlb_misses (0.1% miss rate)
            }
            return values.get(fd)

        try:
            with patch.object(collector, "_read_counter", side_effect=mock_read):
                data = await collector.collect()

            assert data["available"] is True
            # CPU counters
            assert data["cycles"] == 10000000
            assert data["instructions"] == 8000000
            assert data["ipc"] == pytest.approx(0.8)
            # L1D cache
            assert data["l1d_references"] == 5000000
            assert data["l1d_misses"] == 50000
            assert data["l1d_miss_rate"] == pytest.approx(0.01)
            # LLC
            assert data["llc_references"] == 1000000
            assert data["llc_misses"] == 100000
            assert data["llc_miss_rate"] == pytest.approx(0.1)
            # Branch prediction
            assert data["branch_references"] == 2000000
            assert data["branch_misses"] == 40000
            assert data["branch_miss_rate"] == pytest.approx(0.02)
            # DTLB
            assert data["dtlb_references"] == 3000000
            assert data["dtlb_misses"] == 3000
            assert data["dtlb_miss_rate"] == pytest.approx(0.001)
        finally:
            collector._fds = {}


class TestCPUPerfMetricsIntegration:
    """Integration tests for all CPU performance metrics."""

    @pytest.mark.asyncio
    async def test_all_metrics_in_aggregator(self):
        """Test that all CPU performance metrics appear in aggregator output."""
        perf_collector = PerfEventsCollector()
        aggregator = MetricsAggregator(collectors=[perf_collector])

        snapshot = await aggregator.collect_all()

        assert "perf_events" in snapshot
        perf_data = snapshot["perf_events"]
        assert "available" in perf_data

        # All metric fields should exist (may be None if unavailable)
        if perf_data["available"]:
            # CPU counters
            assert "cycles" in perf_data
            assert "instructions" in perf_data
            assert "ipc" in perf_data
            # L1D cache
            assert "l1d_references" in perf_data
            assert "l1d_misses" in perf_data
            assert "l1d_miss_rate" in perf_data
            # LLC
            assert "llc_references" in perf_data
            assert "llc_misses" in perf_data
            assert "llc_miss_rate" in perf_data
            # Branch prediction
            assert "branch_references" in perf_data
            assert "branch_misses" in perf_data
            assert "branch_miss_rate" in perf_data
            # DTLB
            assert "dtlb_references" in perf_data
            assert "dtlb_misses" in perf_data
            assert "dtlb_miss_rate" in perf_data
