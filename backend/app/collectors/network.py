"""Network metrics collector using psutil.

Collects network I/O statistics and per-interface data.
"""

from typing import Any, Dict, List
import logging

import psutil

from app.collectors.base import BaseCollector
from app.utils.rate_calculator import RateCalculator

logger = logging.getLogger(__name__)


class NetworkCollector(BaseCollector):
    """Collector for network metrics using psutil.

    Collects:
    - Total bytes sent/received
    - Bytes per second (calculated from delta)
    - Per-interface statistics
    - Active connection count
    """

    name = "network"

    def __init__(self, enabled: bool = True):
        """Initialize the Network collector.

        Args:
            enabled: Whether this collector is active
        """
        super().__init__(enabled=enabled)
        # Use shared rate calculator
        self._rate_calculator = RateCalculator()

    async def collect(self) -> Dict[str, Any]:
        """Collect network metrics.

        Returns:
            Dictionary containing network metrics.
        """
        # Get network I/O counters
        net_io = psutil.net_io_counters()

        # Calculate rates using RateCalculator
        bytes_sent_per_sec = self._rate_calculator.calculate_rate(
            "bytes_sent", net_io.bytes_sent
        )
        bytes_recv_per_sec = self._rate_calculator.calculate_rate(
            "bytes_recv", net_io.bytes_recv
        )

        result: Dict[str, Any] = {
            "bytes_sent_per_sec": bytes_sent_per_sec,
            "bytes_recv_per_sec": bytes_recv_per_sec,
            "total_bytes_sent": net_io.bytes_sent,
            "total_bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errors_in": net_io.errin,
            "errors_out": net_io.errout,
            "drops_in": net_io.dropin,
            "drops_out": net_io.dropout,
        }

        # Get per-interface stats
        result["interfaces"] = self._get_interface_stats()

        # Get connection count
        result["connection_count"] = self._get_connection_count()

        return result

    def _get_interface_stats(self) -> List[Dict[str, Any]]:
        """Get per-interface network statistics.

        Returns:
            List of interface stat dictionaries.
        """
        try:
            net_io_per_nic = psutil.net_io_counters(pernic=True)
            interfaces = []

            for name, counters in net_io_per_nic.items():
                # Skip loopback interface
                if name == "lo":
                    continue

                interfaces.append({
                    "name": name,
                    "bytes_sent": counters.bytes_sent,
                    "bytes_recv": counters.bytes_recv,
                    "packets_sent": counters.packets_sent,
                    "packets_recv": counters.packets_recv,
                    "errors_in": counters.errin,
                    "errors_out": counters.errout,
                    "drops_in": counters.dropin,
                    "drops_out": counters.dropout,
                })

            return interfaces
        except Exception as e:
            logger.debug(f"Could not get per-interface stats: {e}")
            return []

    def _get_connection_count(self) -> int:
        """Get count of active network connections.

        Returns:
            Number of active connections.
        """
        try:
            connections = psutil.net_connections(kind="inet")
            return len(connections)
        except (psutil.AccessDenied, PermissionError):
            # Connection info requires elevated privileges
            logger.debug("Cannot get connection count: permission denied")
            return -1
        except Exception as e:
            logger.debug(f"Could not get connection count: {e}")
            return -1
