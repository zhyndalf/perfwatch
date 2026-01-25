"""Metrics aggregation and value extraction utilities.

This module contains functions for aggregating metric values, extracting
primary values from different metric types, and downsampling time series data.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from app.models.metrics import MetricsSnapshot


def is_number(value: Any) -> bool:
    """Check if a value is a numeric type (int or float, but not bool)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def calculate_change_percent(
    current: Optional[float], comparison: Optional[float]
) -> Optional[float]:
    """Calculate the percentage change between current and comparison values.

    Args:
        current: The current value
        comparison: The comparison (baseline) value

    Returns:
        The percentage change, or None if calculation is not possible
    """
    if comparison is None or comparison == 0 or current is None:
        return None
    return (current - comparison) / comparison * 100


def aggregate_values(values: List[Any]) -> Any:
    """Aggregate a list of values by averaging numbers or recursively aggregating dicts/lists.

    Args:
        values: List of values to aggregate

    Returns:
        Aggregated value (average for numbers, recursive aggregation for dicts/lists)
    """
    filtered = [value for value in values if value is not None]
    if not filtered:
        return None

    if all(is_number(value) for value in filtered):
        return sum(filtered) / len(filtered)

    if all(isinstance(value, dict) for value in filtered):
        keys = set().union(*(value.keys() for value in filtered))
        return {key: aggregate_values([value.get(key) for value in filtered]) for key in keys}

    if all(isinstance(value, list) for value in filtered):
        lengths = {len(value) for value in filtered}
        if len(lengths) == 1 and all(
            is_number(item) for value in filtered for item in value
        ):
            length = lengths.pop()
            return [
                sum(value[index] for value in filtered) / len(filtered)
                for index in range(length)
            ]
        return filtered[0]

    return filtered[0]


def extract_primary_value(metric_type: str, metric_data: Dict[str, Any]) -> Optional[float]:
    """Extract the primary numeric value from metric data based on metric type.

    Args:
        metric_type: Type of metric (cpu, memory, network, disk, perf_events, memory_bandwidth)
        metric_data: The metric data dictionary

    Returns:
        The primary value as a float, or None if not available
    """
    if metric_type in {"cpu", "memory"}:
        value = metric_data.get("usage_percent")
        return float(value) if is_number(value) else None

    if metric_type == "network":
        sent = metric_data.get("bytes_sent_per_sec")
        recv = metric_data.get("bytes_recv_per_sec")
        if is_number(sent) and is_number(recv):
            return float(sent + recv)
        if is_number(sent):
            return float(sent)
        if is_number(recv):
            return float(recv)
        return None

    if metric_type == "disk":
        io_data = metric_data.get("io") or {}
        read = io_data.get("read_bytes_per_sec")
        write = io_data.get("write_bytes_per_sec")
        if is_number(read) and is_number(write):
            return float(read + write)
        if is_number(read):
            return float(read)
        if is_number(write):
            return float(write)
        return None

    if metric_type == "perf_events":
        events = metric_data.get("events") or {}
        cpu_clock = events.get("cpu-clock", {}).get("value")
        return float(cpu_clock) if is_number(cpu_clock) else None

    if metric_type == "memory_bandwidth":
        value = metric_data.get("page_io_bytes_per_sec")
        return float(value) if is_number(value) else None

    return None


def average_primary(metric_type: str, snapshots: Iterable[MetricsSnapshot]) -> Optional[float]:
    """Calculate the average primary value across a collection of snapshots.

    Args:
        metric_type: Type of metric
        snapshots: Iterable of MetricsSnapshot objects

    Returns:
        Average value, or None if no valid values found
    """
    values: List[float] = []
    for snapshot in snapshots:
        if snapshot.metric_data is None:
            continue
        value = extract_primary_value(metric_type, snapshot.metric_data)
        if value is not None:
            values.append(value)
    if not values:
        return None
    return sum(values) / len(values)


def downsample_snapshots(
    snapshots: List[MetricsSnapshot],
    interval_seconds: int,
    metric_type: str,
) -> List[MetricsSnapshot]:
    """Downsample snapshots by aggregating values within time buckets.

    Args:
        snapshots: List of snapshots to downsample
        interval_seconds: Size of each time bucket in seconds
        metric_type: Type of metric (for creating new snapshot objects)

    Returns:
        List of aggregated snapshots, one per time bucket
    """
    if interval_seconds <= 0 or not snapshots:
        return snapshots

    buckets: Dict[int, List[MetricsSnapshot]] = {}
    for snapshot in snapshots:
        timestamp = snapshot.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        bucket_key = int(timestamp.timestamp() // interval_seconds)
        buckets.setdefault(bucket_key, []).append(snapshot)

    aggregated: List[MetricsSnapshot] = []
    for bucket_key in sorted(buckets.keys()):
        bucket = buckets[bucket_key]
        bucket_time = datetime.fromtimestamp(
            bucket_key * interval_seconds, tz=timezone.utc
        )
        metric_data = aggregate_values([snap.metric_data for snap in bucket]) or {}
        aggregated.append(
            MetricsSnapshot(
                timestamp=bucket_time,
                metric_type=metric_type,
                metric_data=metric_data,
            )
        )

    return aggregated
