"""Service for persisting metrics snapshots to the database.

This module provides functions for saving, querying, and comparing metrics data.
It re-exports aggregation utilities from metrics_aggregation for backward compatibility.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.metrics import MetricsSnapshot

# Re-export aggregation utilities for backward compatibility
from app.services.metrics_aggregation import (
    aggregate_values,
    average_primary,
    calculate_change_percent,
    downsample_snapshots,
    extract_primary_value,
    is_number,
)

logger = logging.getLogger(__name__)

# Backward compatibility aliases (private functions)
_is_number = is_number
_aggregate_values = aggregate_values
_extract_primary_value = extract_primary_value
_average_primary = average_primary
_downsample_snapshots = downsample_snapshots


# =============================================================================
# Interval Resolution
# =============================================================================

_INTERVAL_SECONDS = {
    "5s": 5,
    "1m": 60,
    "5m": 300,
    "1h": 3600,
}

METRIC_TYPES = (
    "cpu",
    "memory",
    "network",
    "disk",
    "perf_events",
    "memory_bandwidth",
)


def resolve_interval(
    start_time: datetime,
    end_time: datetime,
    interval: Optional[str],
) -> Tuple[Optional[str], Optional[int]]:
    """Resolve an interval label and seconds from input and time range.

    Args:
        start_time: Range start
        end_time: Range end
        interval: Requested interval (5s, 1m, 5m, 1h) or "auto"

    Returns:
        Tuple of (interval_label, interval_seconds), or (None, None) if disabled.
    """
    if interval is None:
        return None, None

    interval = interval.lower()
    if interval != "auto":
        if interval not in _INTERVAL_SECONDS:
            raise ValueError(f"Invalid interval: {interval}")
        return interval, _INTERVAL_SECONDS[interval]

    duration_seconds = max((end_time - start_time).total_seconds(), 0)
    if duration_seconds <= 30 * 60:
        return "5s", _INTERVAL_SECONDS["5s"]
    if duration_seconds <= 6 * 60 * 60:
        return "1m", _INTERVAL_SECONDS["1m"]
    if duration_seconds <= 24 * 60 * 60:
        return "5m", _INTERVAL_SECONDS["5m"]
    return "1h", _INTERVAL_SECONDS["1h"]


# =============================================================================
# Metric Row Extraction
# =============================================================================

def _extract_metric_rows(
    snapshot_data: Dict[str, Any],
) -> Tuple[datetime, List[Tuple[str, Dict[str, Any]]]]:
    timestamp_str = snapshot_data.get("timestamp")
    if timestamp_str:
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = timestamp_str
    else:
        timestamp = datetime.utcnow()

    rows = []
    for metric_type in METRIC_TYPES:
        metric_data = snapshot_data.get(metric_type)
        if metric_data is not None:
            rows.append((metric_type, metric_data))

    return timestamp, rows


def _build_snapshots(
    timestamp: datetime,
    rows: List[Tuple[str, Dict[str, Any]]],
) -> List[MetricsSnapshot]:
    return [
        MetricsSnapshot(
            timestamp=timestamp,
            metric_type=metric_type,
            metric_data=metric_data,
        )
        for metric_type, metric_data in rows
    ]


# =============================================================================
# Batch Writer
# =============================================================================

class MetricsBatchWriter:
    """Batch writer for metrics snapshots."""

    def __init__(self, batch_size: int = 50, flush_interval: float = 2.0) -> None:
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._queue: asyncio.Queue = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._stop_marker = object()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def start(self) -> None:
        if self._task is not None:
            return
        self._loop = asyncio.get_running_loop()
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        if self._loop is not None and current_loop is not None and self._loop is not current_loop:
            if self._task.done():
                self._task = None
            return
        await self._queue.put(self._stop_marker)
        await self._task
        self._task = None
        self._running = False

    def is_loop_compatible(self) -> bool:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            return True
        return self._loop is None or self._loop is current_loop

    async def enqueue(self, snapshot_data: Dict[str, Any]) -> None:
        if not self._running:
            return
        timestamp, rows = _extract_metric_rows(snapshot_data)
        if not rows:
            return
        await self._queue.put((timestamp, rows))

    async def _flush(self, pending: List[Tuple[datetime, List[Tuple[str, Dict[str, Any]]]]]) -> None:
        if not pending:
            return

        snapshots: List[MetricsSnapshot] = []
        for timestamp, rows in pending:
            snapshots.extend(_build_snapshots(timestamp, rows))

        try:
            async with AsyncSessionLocal() as session:
                session.add_all(snapshots)
                await session.commit()
        except Exception:
            logger.exception("Failed to flush metrics batch")

    async def _run(self) -> None:
        pending: List[Tuple[datetime, List[Tuple[str, Dict[str, Any]]]]] = []
        while True:
            try:
                item = await asyncio.wait_for(
                    self._queue.get(), timeout=self.flush_interval
                )
            except asyncio.TimeoutError:
                item = None

            if item is self._stop_marker:
                break

            if item is not None:
                pending.append(item)

            if pending and (len(pending) >= self.batch_size or item is None):
                await self._flush(pending)
                pending = []

        if pending:
            await self._flush(pending)


# =============================================================================
# Persistence Functions
# =============================================================================

async def save_metrics_snapshot(
    timestamp: datetime,
    metric_type: str,
    metric_data: Dict[str, Any],
    session: Optional[AsyncSession] = None,
) -> MetricsSnapshot:
    """Save a single metric snapshot to the database.

    Args:
        timestamp: Collection timestamp (UTC)
        metric_type: Type of metric (cpu, memory, network, disk, perf_events, memory_bandwidth)
        metric_data: The metric data as a dictionary
        session: Optional existing session to use

    Returns:
        The created MetricsSnapshot instance
    """
    snapshot = MetricsSnapshot(
        timestamp=timestamp,
        metric_type=metric_type,
        metric_data=metric_data,
    )

    if session:
        session.add(snapshot)
        await session.flush()
    else:
        async with AsyncSessionLocal() as db:
            db.add(snapshot)
            await db.commit()
            await db.refresh(snapshot)

    return snapshot


async def save_all_metrics(
    snapshot_data: Dict[str, Any],
    session: Optional[AsyncSession] = None,
) -> None:
    """Save all metrics from a collection cycle.

    This function extracts individual metric types from the aggregated snapshot
    and saves each one as a separate MetricsSnapshot record.

    Args:
        snapshot_data: The aggregated metrics snapshot containing timestamp and metric data
    """
    timestamp, rows = _extract_metric_rows(snapshot_data)
    if not rows:
        return

    snapshots = _build_snapshots(timestamp, rows)
    if session:
        session.add_all(snapshots)
        await session.flush()
    else:
        async with AsyncSessionLocal() as db_session:
            db_session.add_all(snapshots)
            await db_session.commit()
            logger.debug(f"Saved metrics snapshot for timestamp {timestamp}")


# =============================================================================
# Query Functions
# =============================================================================

async def query_metrics_history(
    metric_type: str,
    start_time: datetime,
    end_time: datetime,
    limit: int = 1000,
    interval: Optional[str] = None,
    session: Optional[AsyncSession] = None,
) -> Tuple[List[MetricsSnapshot], Optional[str]]:
    """Query historical metrics by type and time range.

    Args:
        metric_type: Type of metric to query (cpu, memory, network, disk, perf_events, memory_bandwidth)
        start_time: Start of time range (inclusive)
        end_time: End of time range (inclusive)
        limit: Maximum number of results to return
        interval: Optional aggregation interval (5s, 1m, 5m, 1h, auto)
        session: Optional existing session to use

    Returns:
        Tuple of (MetricsSnapshot list ordered by timestamp ascending, interval label if used)
    """
    interval_label, interval_seconds = resolve_interval(start_time, end_time, interval)

    stmt = (
        select(MetricsSnapshot)
        .where(MetricsSnapshot.metric_type == metric_type)
        .where(MetricsSnapshot.timestamp >= start_time)
        .where(MetricsSnapshot.timestamp <= end_time)
        .order_by(MetricsSnapshot.timestamp.asc())
    )

    if session:
        result = await session.execute(stmt if interval_seconds else stmt.limit(limit))
        snapshots = list(result.scalars().all())
    else:
        async with AsyncSessionLocal() as db:
            result = await db.execute(stmt if interval_seconds else stmt.limit(limit))
            snapshots = list(result.scalars().all())

    if interval_seconds:
        snapshots = _downsample_snapshots(snapshots, interval_seconds, metric_type)

    if limit and len(snapshots) > limit:
        snapshots = snapshots[:limit]

    return snapshots, interval_label


def _resolve_comparison_interval(
    start_time: datetime,
    end_time: datetime,
    interval: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    interval_label, _ = resolve_interval(start_time, end_time, interval)
    interval_value = interval
    if interval is not None and interval.lower() == "auto":
        interval_value = interval_label
    return interval_label, interval_value


async def _compare_metric_ranges(
    *,
    metric_type: str,
    current_start: datetime,
    current_end: datetime,
    comparison_start: datetime,
    comparison_end: datetime,
    limit: int,
    interval: Optional[str],
    session: Optional[AsyncSession],
) -> Tuple[List[MetricsSnapshot], List[MetricsSnapshot], Optional[str], Dict[str, Optional[float]]]:
    interval_label, interval_value = _resolve_comparison_interval(
        current_start, current_end, interval
    )

    current_snapshots, _ = await query_metrics_history(
        metric_type=metric_type,
        start_time=current_start,
        end_time=current_end,
        limit=limit,
        interval=interval_value,
        session=session,
    )

    comparison_snapshots, _ = await query_metrics_history(
        metric_type=metric_type,
        start_time=comparison_start,
        end_time=comparison_end,
        limit=limit,
        interval=interval_value,
        session=session,
    )

    current_avg = _average_primary(metric_type, current_snapshots)
    comparison_avg = _average_primary(metric_type, comparison_snapshots)
    change_percent = calculate_change_percent(current_avg, comparison_avg)

    summary = {
        "current_avg": current_avg,
        "comparison_avg": comparison_avg,
        "change_percent": change_percent,
    }

    return current_snapshots, comparison_snapshots, interval_label, summary


async def compare_metrics_history(
    metric_type: str,
    start_time: datetime,
    end_time: datetime,
    compare_shift: timedelta,
    limit: int = 1000,
    interval: Optional[str] = None,
    session: Optional[AsyncSession] = None,
) -> Tuple[List[MetricsSnapshot], List[MetricsSnapshot], Optional[str], Dict[str, Optional[float]]]:
    comparison_start = start_time - compare_shift
    comparison_end = end_time - compare_shift
    return await _compare_metric_ranges(
        metric_type=metric_type,
        current_start=start_time,
        current_end=end_time,
        comparison_start=comparison_start,
        comparison_end=comparison_end,
        limit=limit,
        interval=interval,
        session=session,
    )


async def compare_metrics_custom_range(
    metric_type: str,
    current_start: datetime,
    current_end: datetime,
    comparison_start: datetime,
    comparison_end: datetime,
    limit: int = 1000,
    interval: Optional[str] = None,
    session: Optional[AsyncSession] = None,
) -> Tuple[List[MetricsSnapshot], List[MetricsSnapshot], Optional[str], Dict[str, Optional[float]]]:
    return await _compare_metric_ranges(
        metric_type=metric_type,
        current_start=current_start,
        current_end=current_end,
        comparison_start=comparison_start,
        comparison_end=comparison_end,
        limit=limit,
        interval=interval,
        session=session,
    )


async def get_latest_metrics(
    metric_type: str,
    limit: int = 1,
    session: Optional[AsyncSession] = None,
) -> List[MetricsSnapshot]:
    """Get the most recent metrics of a given type.

    Args:
        metric_type: Type of metric to query
        limit: Number of recent snapshots to return
        session: Optional existing session to use

    Returns:
        List of MetricsSnapshot objects ordered by timestamp descending
    """
    stmt = (
        select(MetricsSnapshot)
        .where(MetricsSnapshot.metric_type == metric_type)
        .order_by(MetricsSnapshot.timestamp.desc())
        .limit(limit)
    )

    if session:
        result = await session.execute(stmt)
        return list(result.scalars().all())
    else:
        async with AsyncSessionLocal() as db:
            result = await db.execute(stmt)
            return list(result.scalars().all())
