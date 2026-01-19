"""CPU metrics collector using psutil.

Collects CPU usage, per-core stats, frequency, temperature, and load averages.
"""

from typing import Any, Dict, List, Optional
import logging

import psutil

from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class CPUCollector(BaseCollector):
    """Collector for CPU metrics using psutil.

    Collects:
    - Overall CPU usage percentage
    - Per-core usage percentages
    - User/system/idle/iowait time breakdown
    - CPU frequency per core (if available)
    - Load averages (1, 5, 15 minutes)
    - CPU temperature (if sensors available)
    """

    name = "cpu"

    def __init__(self, enabled: bool = True):
        """Initialize the CPU collector.

        Args:
            enabled: Whether this collector is active
        """
        super().__init__(enabled=enabled)
        # Initialize CPU percent tracking (first call returns 0)
        # This primes the measurement for accurate readings
        psutil.cpu_percent(interval=None)
        psutil.cpu_percent(interval=None, percpu=True)

    async def collect(self) -> Dict[str, Any]:
        """Collect CPU metrics.

        Returns:
            Dictionary containing CPU metrics.
        """
        # Get overall CPU usage (non-blocking since we primed it)
        usage_percent = psutil.cpu_percent(interval=None)

        # Get per-core usage
        per_core = psutil.cpu_percent(interval=None, percpu=True)

        # Get CPU times breakdown
        times = psutil.cpu_times_percent(interval=None)

        # Build the result
        result: Dict[str, Any] = {
            "usage_percent": usage_percent,
            "per_core": per_core,
            "user": times.user,
            "system": times.system,
            "idle": times.idle,
            "iowait": getattr(times, "iowait", None),  # Linux only
        }

        # Add optional metrics
        result["frequency_mhz"] = self._get_frequency()
        result["load_avg"] = self._get_load_average()
        result["temperature"] = self._get_temperature()
        result["core_count"] = psutil.cpu_count(logical=True)
        result["physical_cores"] = psutil.cpu_count(logical=False)

        return result

    def _get_frequency(self) -> Optional[List[float]]:
        """Get CPU frequency per core.

        Returns:
            List of frequencies in MHz, or None if unavailable.
        """
        try:
            freq = psutil.cpu_freq(percpu=True)
            if freq:
                return [f.current for f in freq]

            # Some systems only return aggregate frequency
            freq_single = psutil.cpu_freq(percpu=False)
            if freq_single:
                return [freq_single.current]

            return None
        except Exception as e:
            logger.debug(f"Could not get CPU frequency: {e}")
            return None

    def _get_load_average(self) -> Optional[List[float]]:
        """Get system load averages (1, 5, 15 minutes).

        Returns:
            List of [1min, 5min, 15min] load averages, or None if unavailable.
        """
        try:
            if hasattr(psutil, "getloadavg"):
                load = psutil.getloadavg()
                return list(load)
            return None
        except Exception as e:
            logger.debug(f"Could not get load average: {e}")
            return None

    def _get_temperature(self) -> Optional[float]:
        """Get CPU temperature.

        Returns:
            Temperature in Celsius, or None if unavailable.
        """
        try:
            if not hasattr(psutil, "sensors_temperatures"):
                return None

            temps = psutil.sensors_temperatures()
            if not temps:
                return None

            # Try common sensor names
            for name in ["coretemp", "cpu_thermal", "k10temp", "zenpower"]:
                if name in temps:
                    # Get average of all cores
                    readings = [t.current for t in temps[name] if t.current > 0]
                    if readings:
                        return sum(readings) / len(readings)

            # Fallback: try first available sensor
            for sensor_temps in temps.values():
                readings = [t.current for t in sensor_temps if t.current > 0]
                if readings:
                    return sum(readings) / len(readings)

            return None
        except Exception as e:
            logger.debug(f"Could not get CPU temperature: {e}")
            return None
