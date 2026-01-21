"""
Shared constants used across the application.

This module centralizes commonly used constants to avoid duplication
across API endpoints, collectors, and services.
"""

# Valid metric types that can be collected and queried
VALID_METRIC_TYPES = {
    "cpu",
    "memory",
    "network",
    "disk",
    "perf_events",
    "memory_bandwidth",
}

# Valid downsample intervals for historical data aggregation
VALID_DOWNSAMPLE_INTERVALS = {"5s", "1m", "5m", "1h"}

# Valid time periods for historical queries
VALID_PERIODS = {"hour", "day", "week"}

# Valid comparison targets for time-range comparisons
VALID_COMPARE_TO = {"yesterday", "last_week"}

# Minimum and maximum retention days allowed
MIN_RETENTION_DAYS = 1
MAX_RETENTION_DAYS = 365

# Default retention period (days)
DEFAULT_RETENTION_DAYS = 30
