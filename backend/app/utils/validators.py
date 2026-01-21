"""
Shared validation utilities for API endpoints.

This module provides reusable validation functions to avoid duplication
across API route handlers.
"""

from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from app.constants import (
    MAX_RETENTION_DAYS,
    MIN_RETENTION_DAYS,
    VALID_COMPARE_TO,
    VALID_DOWNSAMPLE_INTERVALS,
    VALID_METRIC_TYPES,
    VALID_PERIODS,
)


def validate_metric_type(metric_type: str) -> None:
    """
    Validate that a metric type is supported.

    Args:
        metric_type: The metric type to validate

    Raises:
        HTTPException: If metric type is invalid (400)
    """
    if metric_type not in VALID_METRIC_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric_type. Must be one of: {', '.join(sorted(VALID_METRIC_TYPES))}",
        )


def validate_downsample_interval(interval: Optional[str]) -> None:
    """
    Validate that a downsample interval is valid.

    Args:
        interval: The downsample interval to validate (e.g., "5s", "1m", "5m", "1h")

    Raises:
        HTTPException: If interval is invalid (400)
    """
    if interval is not None and interval not in VALID_DOWNSAMPLE_INTERVALS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid downsample_interval. Must be one of: {', '.join(sorted(VALID_DOWNSAMPLE_INTERVALS))}",
        )


def validate_retention_days(retention_days: int) -> None:
    """
    Validate that retention days is within acceptable range.

    Args:
        retention_days: Number of days to retain metrics

    Raises:
        HTTPException: If retention_days is out of range (400)
    """
    if not MIN_RETENTION_DAYS <= retention_days <= MAX_RETENTION_DAYS:
        raise HTTPException(
            status_code=400,
            detail=f"Retention days must be between {MIN_RETENTION_DAYS} and {MAX_RETENTION_DAYS}",
        )


def validate_time_range(start_time: datetime, end_time: datetime) -> None:
    """
    Validate that a time range is valid (start before end).

    Args:
        start_time: Start of time range
        end_time: End of time range

    Raises:
        HTTPException: If start_time is after end_time (400)
    """
    if start_time >= end_time:
        raise HTTPException(
            status_code=400, detail="start_time must be before end_time"
        )


def validate_period(period: Optional[str]) -> None:
    """
    Validate that a period is valid.

    Args:
        period: Time period (e.g., "hour", "day", "week")

    Raises:
        HTTPException: If period is invalid (400)
    """
    if period is not None and period not in VALID_PERIODS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period. Must be one of: {', '.join(sorted(VALID_PERIODS))}",
        )


def validate_compare_to(compare_to: Optional[str]) -> None:
    """
    Validate that a comparison target is valid.

    Args:
        compare_to: Comparison target (e.g., "yesterday", "last_week")

    Raises:
        HTTPException: If compare_to is invalid (400)
    """
    if compare_to is not None and compare_to not in VALID_COMPARE_TO:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid compare_to. Must be one of: {', '.join(sorted(VALID_COMPARE_TO))}",
        )
