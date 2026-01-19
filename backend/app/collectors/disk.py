"""Disk metrics collector using psutil.

Collects disk I/O statistics and partition usage.
"""

from typing import Any, Dict, List, Optional
import logging
import time

import psutil

from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class DiskCollector(BaseCollector):
    """Collector for disk metrics using psutil.

    Collects:
    - Partition usage (total, used, free, percent)
    - Disk I/O (read/write bytes, counts, times)
    - I/O rates (bytes per second)
    """

    name = "disk"

    def __init__(self, enabled: bool = True):
        """Initialize the Disk collector.

        Args:
            enabled: Whether this collector is active
        """
        super().__init__(enabled=enabled)
        # Store last values for rate calculation
        self._last_io: Optional[Dict[str, Any]] = None
        self._last_time: Optional[float] = None

    async def collect(self) -> Dict[str, Any]:
        """Collect disk metrics.

        Returns:
            Dictionary containing disk metrics.
        """
        result: Dict[str, Any] = {
            "partitions": self._get_partition_usage(),
            "io": self._get_io_stats(),
        }

        return result

    def _get_partition_usage(self) -> List[Dict[str, Any]]:
        """Get disk partition usage statistics.

        Returns:
            List of partition stat dictionaries.
        """
        partitions = []

        try:
            for partition in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_bytes": usage.total,
                        "used_bytes": usage.used,
                        "free_bytes": usage.free,
                        "usage_percent": usage.percent,
                    })
                except (PermissionError, OSError) as e:
                    # Some partitions may not be accessible
                    logger.debug(f"Could not get usage for {partition.mountpoint}: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Could not get disk partitions: {e}")

        return partitions

    def _get_io_stats(self) -> Dict[str, Any]:
        """Get disk I/O statistics with rate calculation.

        Returns:
            Dictionary with I/O stats.
        """
        current_time = time.time()

        try:
            io_counters = psutil.disk_io_counters()
            if io_counters is None:
                return self._empty_io_stats()

            # Calculate rates
            read_bytes_per_sec = 0.0
            write_bytes_per_sec = 0.0

            if self._last_io and self._last_time:
                time_delta = current_time - self._last_time
                if time_delta > 0:
                    read_bytes_per_sec = (io_counters.read_bytes - self._last_io["read_bytes"]) / time_delta
                    write_bytes_per_sec = (io_counters.write_bytes - self._last_io["write_bytes"]) / time_delta

            # Update last values
            self._last_io = {
                "read_bytes": io_counters.read_bytes,
                "write_bytes": io_counters.write_bytes,
            }
            self._last_time = current_time

            return {
                "read_bytes_per_sec": max(0, read_bytes_per_sec),
                "write_bytes_per_sec": max(0, write_bytes_per_sec),
                "read_bytes": io_counters.read_bytes,
                "write_bytes": io_counters.write_bytes,
                "read_count": io_counters.read_count,
                "write_count": io_counters.write_count,
                "read_time_ms": io_counters.read_time,
                "write_time_ms": io_counters.write_time,
            }

        except Exception as e:
            logger.warning(f"Could not get disk I/O stats: {e}")
            return self._empty_io_stats()

    def _empty_io_stats(self) -> Dict[str, Any]:
        """Return empty I/O stats structure."""
        return {
            "read_bytes_per_sec": 0.0,
            "write_bytes_per_sec": 0.0,
            "read_bytes": 0,
            "write_bytes": 0,
            "read_count": 0,
            "write_count": 0,
            "read_time_ms": 0,
            "write_time_ms": 0,
        }
