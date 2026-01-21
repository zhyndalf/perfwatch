"""Memory bandwidth collector using /proc/vmstat.

This collector tracks memory I/O activity by monitoring page-in/page-out
operations from /proc/vmstat. This provides a proxy for memory bandwidth
that works universally on Linux systems, including Docker containers.

Note: This measures disk ↔ memory I/O, not CPU ↔ memory bandwidth.
True memory bandwidth requires uncore IMC counters which need special
permissions typically not available in containers.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from app.collectors.base import BaseCollector
from app.utils.rate_calculator import RateCalculator

logger = logging.getLogger(__name__)

# Path to vmstat
VMSTAT_PATH = Path("/proc/vmstat")


class MemoryBandwidthCollector(BaseCollector):
    """Collector for memory I/O bandwidth from /proc/vmstat.

    Collects:
    - pgpgin_per_sec: Kilobytes paged in per second (disk → memory)
    - pgpgout_per_sec: Kilobytes paged out per second (memory → disk)
    - pswpin_per_sec: Pages swapped in per second
    - pswpout_per_sec: Pages swapped out per second
    - page_io_bytes_per_sec: Total page I/O rate in bytes/sec

    These metrics track disk ↔ memory I/O activity and serve as a proxy
    for memory bandwidth. High values indicate memory pressure or active
    file I/O operations.

    The collector gracefully returns {"available": False} if /proc/vmstat
    is not accessible.

    Attributes:
        name: Collector identifier ('memory_bandwidth')
        enabled: Whether the collector is active
    """

    name = "memory_bandwidth"

    def __init__(self, enabled: bool = True):
        """Initialize the memory bandwidth collector.

        Args:
            enabled: Whether this collector should be active
        """
        super().__init__(enabled=enabled)
        self._rate_calculator = RateCalculator()
        self._available: Optional[bool] = None

    def _parse_vmstat(self) -> Optional[Dict[str, int]]:
        """Parse /proc/vmstat and extract relevant metrics.

        Returns:
            Dictionary with vmstat values, or None if unavailable.
        """
        try:
            if not VMSTAT_PATH.exists():
                logger.debug("memory_bandwidth: /proc/vmstat not found")
                return None

            content = VMSTAT_PATH.read_text()
            values = {}

            for line in content.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    key, value = parts[0], parts[1]
                    # Only extract the metrics we care about
                    if key in ("pgpgin", "pgpgout", "pswpin", "pswpout",
                               "pgfault", "pgmajfault"):
                        try:
                            values[key] = int(value)
                        except ValueError:
                            pass

            # Ensure we got the essential metrics
            if "pgpgin" in values and "pgpgout" in values:
                return values

            logger.debug("memory_bandwidth: Missing required metrics in vmstat")
            return None

        except Exception as e:
            logger.debug(f"memory_bandwidth: Failed to parse vmstat: {e}")
            return None

    def is_available(self) -> bool:
        """Check if memory bandwidth metrics are available.

        Returns:
            True if /proc/vmstat is accessible, False otherwise.
        """
        if self._available is None:
            self._available = self._parse_vmstat() is not None
        return self._available

    async def collect(self) -> Dict[str, Any]:
        """Collect memory bandwidth metrics.

        Returns:
            Dictionary containing:
            - available: bool - Whether metrics are available
            - pgpgin_per_sec: float - KB paged in per second (if available)
            - pgpgout_per_sec: float - KB paged out per second (if available)
            - pswpin_per_sec: float - Pages swapped in per second (if available)
            - pswpout_per_sec: float - Pages swapped out per second (if available)
            - page_io_bytes_per_sec: float - Total page I/O in bytes/sec
            - pgfault_per_sec: float - Page faults per second (if available)
            - pgmajfault_per_sec: float - Major page faults per second (if available)
            - swap_io_bytes_per_sec: float - Swap I/O in bytes/sec

            Note: First call returns zeros (needs two readings to calculate rates).
        """
        current_values = self._parse_vmstat()

        if current_values is None:
            self._available = False
            return {"available": False}

        self._available = True

        # Calculate rates using RateCalculator
        pgpgin_per_sec = self._rate_calculator.calculate_rate(
            "pgpgin", current_values.get("pgpgin", 0)
        )
        pgpgout_per_sec = self._rate_calculator.calculate_rate(
            "pgpgout", current_values.get("pgpgout", 0)
        )
        pswpin_per_sec = self._rate_calculator.calculate_rate(
            "pswpin", current_values.get("pswpin", 0)
        )
        pswpout_per_sec = self._rate_calculator.calculate_rate(
            "pswpout", current_values.get("pswpout", 0)
        )
        pgfault_per_sec = self._rate_calculator.calculate_rate(
            "pgfault", current_values.get("pgfault", 0)
        )
        pgmajfault_per_sec = self._rate_calculator.calculate_rate(
            "pgmajfault", current_values.get("pgmajfault", 0)
        )

        # pgpgin/pgpgout are in KB, convert to bytes for total
        # page_io is disk ↔ memory I/O (not swap)
        page_io_bytes_per_sec = (pgpgin_per_sec + pgpgout_per_sec) * 1024

        # Swap I/O: pswpin/pswpout are in pages (typically 4KB)
        page_size = 4096  # Standard page size
        swap_io_bytes_per_sec = (pswpin_per_sec + pswpout_per_sec) * page_size

        return {
            "available": True,
            # Page I/O rates (KB/sec from vmstat)
            "pgpgin_per_sec": round(pgpgin_per_sec, 2),
            "pgpgout_per_sec": round(pgpgout_per_sec, 2),
            # Swap rates (pages/sec)
            "pswpin_per_sec": round(pswpin_per_sec, 2),
            "pswpout_per_sec": round(pswpout_per_sec, 2),
            # Aggregated metrics (bytes/sec)
            "page_io_bytes_per_sec": round(page_io_bytes_per_sec, 2),
            "swap_io_bytes_per_sec": round(swap_io_bytes_per_sec, 2),
            # Page fault rates
            "pgfault_per_sec": round(pgfault_per_sec, 2),
            "pgmajfault_per_sec": round(pgmajfault_per_sec, 2),
        }

    def reset(self) -> None:
        """Reset the collector state.

        Clears cached values, useful for testing or re-initialization.
        """
        self._rate_calculator.reset()
        self._available = None
