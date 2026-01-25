"""History API endpoints for querying historical metrics data."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DbSession
from app.constants import VALID_METRIC_TYPES
from app.services.metrics_storage import (
    compare_metrics_custom_range,
    compare_metrics_history,
    query_metrics_history,
    resolve_interval,
)
from app.utils.validators import validate_compare_to, validate_metric_type, validate_period, validate_time_range


router = APIRouter(prefix="/api/history", tags=["history"])


# Helper data classes for comparison operations
class ComparisonParams:
    """Parameters for a comparison query."""

    def __init__(
        self,
        current_start: datetime,
        current_end: datetime,
        comparison_start: datetime,
        comparison_end: datetime,
        period_label: str,
        compare_label: str,
        compare_shift: Optional[timedelta] = None,
    ):
        self.current_start = current_start
        self.current_end = current_end
        self.comparison_start = comparison_start
        self.comparison_end = comparison_end
        self.period_label = period_label
        self.compare_label = compare_label
        self.compare_shift = compare_shift


def _validate_custom_comparison(
    start_time_1: Optional[datetime],
    end_time_1: Optional[datetime],
    start_time_2: Optional[datetime],
    end_time_2: Optional[datetime],
) -> ComparisonParams:
    """Validate and prepare custom comparison parameters.

    Raises:
        HTTPException: If validation fails
    """
    if not all(p is not None for p in [start_time_1, end_time_1, start_time_2, end_time_2]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time_1, end_time_1, start_time_2, end_time_2 are required for custom comparison",
        )
    validate_time_range(start_time_1, end_time_1)
    validate_time_range(start_time_2, end_time_2)
    if (end_time_1 - start_time_1) != (end_time_2 - start_time_2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom comparison periods must have the same duration",
        )
    return ComparisonParams(
        current_start=start_time_1,
        current_end=end_time_1,
        comparison_start=start_time_2,
        comparison_end=end_time_2,
        period_label="custom",
        compare_label="custom",
    )


def _validate_relative_comparison(
    period: Optional[str],
    compare_to: Optional[str],
) -> ComparisonParams:
    """Validate and prepare relative comparison parameters.

    Raises:
        HTTPException: If validation fails
    """
    if period is None or compare_to is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="period and compare_to are required for relative comparison",
        )
    period = period.lower()
    compare_to = compare_to.lower()
    validate_period(period)
    validate_compare_to(compare_to)

    now = datetime.now(timezone.utc)
    delta = {
        "hour": timedelta(hours=1),
        "day": timedelta(days=1),
        "week": timedelta(days=7),
    }.get(period, timedelta(days=1))

    compare_shift = timedelta(days=1) if compare_to == "yesterday" else timedelta(days=7)
    current_start = now - delta
    current_end = now

    return ComparisonParams(
        current_start=current_start,
        current_end=current_end,
        comparison_start=current_start - compare_shift,
        comparison_end=current_end - compare_shift,
        period_label=period,
        compare_label=compare_to,
        compare_shift=compare_shift,
    )


def _validate_interval(start: datetime, end: datetime, interval: Optional[str]) -> Optional[str]:
    """Validate and resolve interval, raising HTTPException on error."""
    try:
        interval_label, _ = resolve_interval(start, end, interval)
        return interval_label
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def _build_comparison_response(
    metric_type: str,
    params: ComparisonParams,
    current_snapshots: list,
    comparison_snapshots: list,
    interval_used: Optional[str],
    interval_label: Optional[str],
    summary: dict,
) -> ComparisonResponse:
    """Build the comparison response from query results."""
    current_points = [
        HistoryDataPoint(timestamp=s.timestamp, data=s.metric_data)
        for s in current_snapshots
    ]
    comparison_points = [
        HistoryDataPoint(timestamp=s.timestamp, data=s.metric_data)
        for s in comparison_snapshots
    ]

    return ComparisonResponse(
        metric_type=metric_type,
        period=params.period_label,
        compare_to=params.compare_label,
        interval=interval_used or interval_label,
        current=ComparisonSeries(
            start_time=params.current_start,
            end_time=params.current_end,
            data_points=current_points,
        ),
        comparison=ComparisonSeries(
            start_time=params.comparison_start,
            end_time=params.comparison_end,
            data_points=comparison_points,
        ),
        summary=ComparisonSummary(**summary),
    )


class HistoryDataPoint(BaseModel):
    """A single historical data point."""

    timestamp: datetime = Field(..., description="Data point timestamp")
    data: Dict[str, Any] = Field(..., description="Metric data")


class HistoryResponse(BaseModel):
    """Response schema for historical metrics query."""

    metric_type: str = Field(..., description="Type of metric")
    start_time: datetime = Field(..., description="Query start time")
    end_time: datetime = Field(..., description="Query end time")
    interval: Optional[str] = Field(None, description="Aggregation interval used")
    count: int = Field(..., description="Number of data points returned")
    data_points: List[HistoryDataPoint] = Field(
        default_factory=list, description="Historical data points"
    )


class ComparisonSeries(BaseModel):
    """Series data for comparison responses."""

    start_time: datetime
    end_time: datetime
    data_points: List[HistoryDataPoint] = Field(default_factory=list)


class ComparisonSummary(BaseModel):
    """Summary stats for comparison responses."""

    current_avg: Optional[float] = None
    comparison_avg: Optional[float] = None
    change_percent: Optional[float] = None


class ComparisonResponse(BaseModel):
    """Response schema for comparison query."""

    metric_type: str
    period: str
    compare_to: str
    interval: Optional[str] = None
    current: ComparisonSeries
    comparison: ComparisonSeries
    summary: ComparisonSummary


@router.get("/metrics", response_model=HistoryResponse)
async def get_metrics_history(
    current_user: CurrentUser,
    db: DbSession,
    metric_type: str = Query(..., description="Metric type to query"),
    start_time: datetime = Query(..., description="Start of time range (ISO 8601)"),
    end_time: datetime = Query(..., description="End of time range (ISO 8601)"),
    limit: int = Query(default=1000, ge=1, le=10000, description="Maximum results to return"),
    interval: Optional[str] = Query(
        default="auto",
        description="Aggregation interval: 5s, 1m, 5m, 1h, auto",
    ),
) -> HistoryResponse:
    """Query historical metrics by type and time range.

    Requires authentication. Returns metrics snapshots within the specified
    time range, ordered by timestamp ascending.

    **Query Parameters:**
    - `metric_type` (required): One of cpu, memory, network, disk, perf_events, memory_bandwidth
    - `start_time` (required): Start of time range in ISO 8601 format
    - `end_time` (required): End of time range in ISO 8601 format
    - `limit` (optional): Maximum number of results (default: 1000, max: 10000)

    **Example:**
    ```
    GET /api/history/metrics?metric_type=cpu&start_time=2026-01-20T00:00:00Z&end_time=2026-01-20T23:59:59Z
    ```
    """
    # Validate inputs
    validate_metric_type(metric_type)
    validate_time_range(start_time, end_time)

    # Validate interval
    try:
        interval_label, _ = resolve_interval(start_time, end_time, interval)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # Query the database
    snapshots, interval_used = await query_metrics_history(
        metric_type=metric_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        interval=interval,
        session=db,
    )

    # Transform to response format
    data_points = [
        HistoryDataPoint(timestamp=s.timestamp, data=s.metric_data)
        for s in snapshots
    ]

    return HistoryResponse(
        metric_type=metric_type,
        start_time=start_time,
        end_time=end_time,
        interval=interval_used or interval_label,
        count=len(data_points),
        data_points=data_points,
    )


@router.get("/metrics/types")
async def get_available_metric_types(
    current_user: CurrentUser,
) -> Dict[str, List[str]]:
    """Get list of available metric types.

    Returns the valid metric types that can be queried via the history API.
    """
    return {"metric_types": sorted(VALID_METRIC_TYPES)}


@router.get("/compare", response_model=ComparisonResponse)
async def compare_metrics(
    current_user: CurrentUser,
    db: DbSession,
    metric_type: str = Query(..., description="Metric type to query"),
    period: Optional[str] = Query(None, description="Comparison period: hour, day, week"),
    compare_to: Optional[str] = Query(None, description="Comparison target: yesterday, last_week"),
    limit: int = Query(default=1000, ge=1, le=10000, description="Maximum results to return"),
    interval: Optional[str] = Query(
        default="auto",
        description="Aggregation interval: 5s, 1m, 5m, 1h, auto",
    ),
    start_time_1: Optional[datetime] = Query(
        None, description="Custom comparison start time for period 1 (ISO 8601)"
    ),
    end_time_1: Optional[datetime] = Query(
        None, description="Custom comparison end time for period 1 (ISO 8601)"
    ),
    start_time_2: Optional[datetime] = Query(
        None, description="Custom comparison start time for period 2 (ISO 8601)"
    ),
    end_time_2: Optional[datetime] = Query(
        None, description="Custom comparison end time for period 2 (ISO 8601)"
    ),
) -> ComparisonResponse:
    """Compare metrics between two time periods.

    Supports both custom time ranges and relative comparisons (yesterday, last_week).
    """
    validate_metric_type(metric_type)

    custom_params = [start_time_1, end_time_1, start_time_2, end_time_2]
    has_custom_range = any(param is not None for param in custom_params)

    if has_custom_range:
        params = _validate_custom_comparison(start_time_1, end_time_1, start_time_2, end_time_2)
        interval_label = _validate_interval(params.current_start, params.current_end, interval)
        (
            current_snapshots,
            comparison_snapshots,
            interval_used,
            summary,
        ) = await compare_metrics_custom_range(
            metric_type=metric_type,
            current_start=params.current_start,
            current_end=params.current_end,
            comparison_start=params.comparison_start,
            comparison_end=params.comparison_end,
            limit=limit,
            interval=interval,
            session=db,
        )
    else:
        params = _validate_relative_comparison(period, compare_to)
        interval_label = _validate_interval(params.current_start, params.current_end, interval)
        current_snapshots, comparison_snapshots, interval_used, summary = (
            await compare_metrics_history(
                metric_type=metric_type,
                start_time=params.current_start,
                end_time=params.current_end,
                compare_shift=params.compare_shift,
                limit=limit,
                interval=interval,
                session=db,
            )
        )

    return _build_comparison_response(
        metric_type=metric_type,
        params=params,
        current_snapshots=current_snapshots,
        comparison_snapshots=comparison_snapshots,
        interval_used=interval_used,
        interval_label=interval_label,
        summary=summary,
    )
