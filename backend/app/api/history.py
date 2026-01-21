"""History API endpoints for querying historical metrics data."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DbSession
from app.constants import VALID_METRIC_TYPES
from app.services.metrics_storage import compare_metrics_history, query_metrics_history, resolve_interval
from app.utils.validators import validate_compare_to, validate_metric_type, validate_period, validate_time_range


router = APIRouter(prefix="/api/history", tags=["history"])


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
    period: str = Query(..., description="Comparison period: hour, day, week"),
    compare_to: str = Query(..., description="Comparison target: yesterday, last_week"),
    limit: int = Query(default=1000, ge=1, le=10000, description="Maximum results to return"),
    interval: Optional[str] = Query(
        default="auto",
        description="Aggregation interval: 5s, 1m, 5m, 1h, auto",
    ),
) -> ComparisonResponse:
    # Validate inputs
    validate_metric_type(metric_type)

    period = period.lower()
    compare_to = compare_to.lower()
    validate_period(period)
    validate_compare_to(compare_to)

    now = datetime.now(timezone.utc)
    if period == "hour":
        delta = timedelta(hours=1)
    elif period == "day":
        delta = timedelta(days=1)
    else:
        delta = timedelta(days=7)

    if compare_to == "yesterday":
        compare_shift = timedelta(days=1)
    else:
        compare_shift = timedelta(days=7)

    start_time = now - delta
    end_time = now

    try:
        interval_label, _ = resolve_interval(start_time, end_time, interval)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    current_snapshots, comparison_snapshots, interval_used, summary = await compare_metrics_history(
        metric_type=metric_type,
        start_time=start_time,
        end_time=end_time,
        compare_shift=compare_shift,
        limit=limit,
        interval=interval,
        session=db,
    )

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
        period=period,
        compare_to=compare_to,
        interval=interval_used or interval_label,
        current=ComparisonSeries(
            start_time=start_time,
            end_time=end_time,
            data_points=current_points,
        ),
        comparison=ComparisonSeries(
            start_time=start_time - compare_shift,
            end_time=end_time - compare_shift,
            data_points=comparison_points,
        ),
        summary=ComparisonSummary(**summary),
    )
