"""
Shared rate calculation utility for metrics collectors.

This module provides a reusable rate calculator to avoid duplication
across network, disk, and memory bandwidth collectors.
"""

import time
from typing import Dict, Optional


class RateCalculator:
    """
    Calculate per-second rates for counter metrics.

    Maintains state for last values and timestamps to compute
    rates between successive measurements.

    Example:
        calculator = RateCalculator()
        rate = calculator.calculate_rate("bytes_sent", 1024)  # Returns 0.0 on first call
        time.sleep(1)
        rate = calculator.calculate_rate("bytes_sent", 2048)  # Returns ~1024.0
    """

    def __init__(self):
        """Initialize the rate calculator."""
        self._last_counters: Dict[str, float] = {}
        self._last_times: Dict[str, float] = {}

    def calculate_rate(self, key: str, current_value: float) -> float:
        """
        Calculate the per-second rate for a counter metric.

        Args:
            key: Unique identifier for this metric (e.g., "bytes_sent")
            current_value: Current counter value

        Returns:
            Rate per second. Returns 0.0 on first call or if time_delta <= 0.
            Returns max(0, rate) to handle counter wraparounds gracefully.
        """
        current_time = time.time()

        # First call for this key - store and return 0
        if key not in self._last_counters or key not in self._last_times:
            self._last_counters[key] = current_value
            self._last_times[key] = current_time
            return 0.0

        # Calculate time delta
        time_delta = current_time - self._last_times[key]
        if time_delta <= 0:
            # Avoid division by zero or negative deltas
            return 0.0

        # Calculate value delta
        value_delta = current_value - self._last_counters[key]

        # Store current values for next calculation
        self._last_counters[key] = current_value
        self._last_times[key] = current_time

        # Calculate rate, handling counter wraparound
        rate = value_delta / time_delta

        # Return max(0, rate) to gracefully handle counter resets
        return max(0.0, rate)

    def calculate_rates(self, counters: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate rates for multiple counters at once.

        Args:
            counters: Dictionary of {metric_name: current_value}

        Returns:
            Dictionary of {metric_name: rate_per_sec}

        Example:
            rates = calculator.calculate_rates({
                "bytes_sent": 1024,
                "bytes_recv": 2048,
            })
            # Returns: {"bytes_sent": 512.0, "bytes_recv": 1024.0}
        """
        return {key: self.calculate_rate(key, value) for key, value in counters.items()}

    def reset(self, key: Optional[str] = None) -> None:
        """
        Reset stored state for rate calculations.

        Args:
            key: If provided, reset only this metric. Otherwise, reset all.

        Useful for testing or when metrics are re-initialized.
        """
        if key is not None:
            self._last_counters.pop(key, None)
            self._last_times.pop(key, None)
        else:
            self._last_counters.clear()
            self._last_times.clear()
