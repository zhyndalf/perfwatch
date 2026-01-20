"""Retention policy API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.config import settings
from app.schemas.retention import (
    RetentionCleanupResponse,
    RetentionPolicyResponse,
    RetentionPolicyUpdate,
)
from app.services.retention import (
    apply_retention_policy,
    get_retention_policy,
    update_retention_policy,
)


router = APIRouter(prefix="/api/retention", tags=["retention"])

VALID_DOWNSAMPLE_INTERVALS = {"5s", "1m", "5m", "1h"}


@router.get("", response_model=RetentionPolicyResponse)
async def get_retention(current_user: CurrentUser, db: DbSession) -> RetentionPolicyResponse:
    """Get the current retention policy."""
    policy = await get_retention_policy(db)
    return RetentionPolicyResponse(
        id=policy.id,
        retention_days=policy.retention_days,
        archive_enabled=policy.archive_enabled,
        downsample_after_days=policy.downsample_after_days,
        downsample_interval=policy.downsample_interval,
        last_archive_run=policy.last_archive_run,
        created_at=policy.created_at,
        updated_at=policy.updated_at,
        cleanup_enabled=settings.RETENTION_CLEANUP_ENABLED,
        cleanup_interval_minutes=settings.RETENTION_CLEANUP_INTERVAL_MINUTES,
    )


@router.put("", response_model=RetentionPolicyResponse)
async def update_retention(
    current_user: CurrentUser,
    db: DbSession,
    payload: RetentionPolicyUpdate,
) -> RetentionPolicyResponse:
    """Update retention policy settings."""
    if payload.downsample_interval and payload.downsample_interval not in VALID_DOWNSAMPLE_INTERVALS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid downsample_interval. Must be one of: {', '.join(sorted(VALID_DOWNSAMPLE_INTERVALS))}",
        )

    existing = await get_retention_policy(db)
    effective_retention = payload.retention_days or existing.retention_days
    effective_downsample = payload.downsample_after_days
    if effective_downsample is None:
        effective_downsample = existing.downsample_after_days
    if effective_downsample > effective_retention:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="downsample_after_days must be less than or equal to retention_days",
        )

    if payload.cleanup_interval_minutes is not None and payload.cleanup_interval_minutes < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cleanup_interval_minutes must be at least 1",
        )

    if payload.cleanup_enabled is not None:
        settings.RETENTION_CLEANUP_ENABLED = payload.cleanup_enabled
    if payload.cleanup_interval_minutes is not None:
        settings.RETENTION_CLEANUP_INTERVAL_MINUTES = payload.cleanup_interval_minutes

    policy = await update_retention_policy(
        db,
        retention_days=payload.retention_days,
        archive_enabled=payload.archive_enabled,
        downsample_after_days=payload.downsample_after_days,
        downsample_interval=payload.downsample_interval,
    )
    return RetentionPolicyResponse(
        id=policy.id,
        retention_days=policy.retention_days,
        archive_enabled=policy.archive_enabled,
        downsample_after_days=policy.downsample_after_days,
        downsample_interval=policy.downsample_interval,
        last_archive_run=policy.last_archive_run,
        created_at=policy.created_at,
        updated_at=policy.updated_at,
        cleanup_enabled=settings.RETENTION_CLEANUP_ENABLED,
        cleanup_interval_minutes=settings.RETENTION_CLEANUP_INTERVAL_MINUTES,
    )


@router.post("/cleanup", response_model=RetentionCleanupResponse)
async def run_retention_cleanup(
    current_user: CurrentUser,
    db: DbSession,
) -> RetentionCleanupResponse:
    """Run retention cleanup immediately."""
    deleted_count, downsampled_count = await apply_retention_policy(db)
    policy = await get_retention_policy(db)
    return RetentionCleanupResponse(
        deleted_count=deleted_count,
        downsampled_count=downsampled_count,
        last_archive_run=policy.last_archive_run,
    )
