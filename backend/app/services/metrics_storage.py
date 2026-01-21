"""Service for persisting metrics snapshots to the database."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.metrics import MetricsSnapshot

logger = logging.getLogger(__name__)

_INTERVAL_SECONDS = {
    "5s": 5,
    "1m": 60,
    "5m": 300,
    "1h": 3600,
}


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


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _aggregate_values(values: List[Any]) -> Any:
    filtered = [value for value in values if value is not None]
    if not filtered:
        return None

    if all(_is_number(value) for value in filtered):
        return sum(filtered) / len(filtered)

    if all(isinstance(value, dict) for value in filtered):
        keys = set().union(*(value.keys() for value in filtered))
        return {key: _aggregate_values([value.get(key) for value in filtered]) for key in keys}

    if all(isinstance(value, list) for value in filtered):
        lengths = {len(value) for value in filtered}
        if len(lengths) == 1 and all(
            _is_number(item) for value in filtered for item in value
        ):
            length = lengths.pop()
            return [
                sum(value[index] for value in filtered) / len(filtered)
                for index in range(length)
            ]
        return filtered[0]

    return filtered[0]


def _extract_primary_value(metric_type: str, metric_data: Dict[str, Any]) -> Optional[float]:
    if metric_type in {"cpu", "memory"}:
        value = metric_data.get("usage_percent")
        return float(value) if _is_number(value) else None
    if metric_type == "network":
        sent = metric_data.get("bytes_sent_per_sec")
        recv = metric_data.get("bytes_recv_per_sec")
        if _is_number(sent) and _is_number(recv):
            return float(sent + recv)
        if _is_number(sent):
            return float(sent)
        if _is_number(recv):
            return float(recv)
        return None
    if metric_type == "disk":
        io_data = metric_data.get("io") or {}
        read = io_data.get("read_bytes_per_sec")
        write = io_data.get("write_bytes_per_sec")
        if _is_number(read) and _is_number(write):
            return float(read + write)
        if _is_number(read):
            return float(read)
        if _is_number(write):
            return float(write)
        return None
    if metric_type == "perf_events":
        value = metric_data.get("ipc")
        return float(value) if _is_number(value) else None
    if metric_type == "memory_bandwidth":
        value = metric_data.get("page_io_bytes_per_sec")
        return float(value) if _is_number(value) else None
    return None


def _average_primary(metric_type: str, snapshots: Iterable[MetricsSnapshot]) -> Optional[float]:
    values: List[float] = []
    for snapshot in snapshots:
        if snapshot.metric_data is None:
            continue
        value = _extract_primary_value(metric_type, snapshot.metric_data)
        if value is not None:
            values.append(value)
    if not values:
        return None
    return sum(values) / len(values)


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

    metric_types = ["cpu", "memory", "network", "disk", "perf_events", "memory_bandwidth"]
    rows = []
    for metric_type in metric_types:
        metric_data = snapshot_data.get(metric_type)
        if metric_data is not None:
            rows.append((metric_type, metric_data))

    return timestamp, rows


def _downsample_snapshots(
    snapshots: List[MetricsSnapshot],
    interval_seconds: int,
    metric_type: str,
) -> List[MetricsSnapshot]:
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
        metric_data = _aggregate_values([snap.metric_data for snap in bucket]) or {}
        aggregated.append(
            MetricsSnapshot(
                timestamp=bucket_time,
                metric_type=metric_type,
                metric_data=metric_data,
            )
        )

    return aggregated


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
            for metric_type, metric_data in rows:
                snapshots.append(
                    MetricsSnapshot(
                        timestamp=timestamp,
                        metric_type=metric_type,
                        metric_data=metric_data,
                    )
                )

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

    if session:
        for metric_type, metric_data in rows:
            snapshot = MetricsSnapshot(
                timestamp=timestamp,
                metric_type=metric_type,
                metric_data=metric_data,
            )
            session.add(snapshot)
        await session.flush()
    else:
        async with AsyncSessionLocal() as db_session:
            for metric_type, metric_data in rows:
                snapshot = MetricsSnapshot(
                    timestamp=timestamp,
                    metric_type=metric_type,
                    metric_data=metric_data,
                )
                db_session.add(snapshot)

            await db_session.commit()
            logger.debug(f"Saved metrics snapshot for timestamp {timestamp}")


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

    current_snapshots, interval_label = await query_metrics_history(
        metric_type=metric_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        interval=interval,
        session=session,
    )

    comparison_snapshots, _ = await query_metrics_history(
        metric_type=metric_type,
        start_time=comparison_start,
        end_time=comparison_end,
        limit=limit,
        interval=interval,
        session=session,
    )

    current_avg = _average_primary(metric_type, current_snapshots)
    comparison_avg = _average_primary(metric_type, comparison_snapshots)
    if comparison_avg is None or comparison_avg == 0:
        change_percent = None
    elif current_avg is None:
        change_percent = None
    else:
        change_percent = (current_avg - comparison_avg) / comparison_avg * 100

    summary = {
        "current_avg": current_avg,
        "comparison_avg": comparison_avg,
        "change_percent": change_percent,
    }

    return current_snapshots, comparison_snapshots, interval_label, summary


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
    interval_label, _ = resolve_interval(current_start, current_end, interval)
    interval_value = interval
    if interval is not None and interval.lower() == "auto":
        interval_value = interval_label

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
    if comparison_avg is None or comparison_avg == 0:
        change_percent = None
    elif current_avg is None:
        change_percent = None
    else:
        change_percent = (current_avg - comparison_avg) / comparison_avg * 100

    summary = {
        "current_avg": current_avg,
        "comparison_avg": comparison_avg,
        "change_percent": change_percent,
    }

    return current_snapshots, comparison_snapshots, interval_label, summary


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
