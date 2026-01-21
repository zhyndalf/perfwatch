"""Configuration API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.config import settings
from app.schemas.config import ConfigResponse, ConfigUpdate, ConfigUpdateResponse
from app.services.config import get_config_values, update_config_values
from app.services.retention import get_retention_policy, update_retention_policy
from app.utils.validators import validate_downsample_interval


router = APIRouter(prefix="/api/config", tags=["config"])


def _validate_retention_update(
    retention_days: int,
    downsample_after_days: int,
    downsample_interval: str,
) -> None:
    validate_downsample_interval(downsample_interval)
    if downsample_after_days > retention_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="downsample_after_days must be less than or equal to retention_days",
        )


@router.get("", response_model=ConfigResponse)
async def get_config(
    current_user: CurrentUser,
    db: DbSession,
) -> ConfigResponse:
    """Get current configuration values."""
    config = await get_config_values(db)
    retention = await get_retention_policy(db)

    sampling_interval_seconds = config["sampling"].get(
        "interval_seconds", settings.SAMPLING_INTERVAL_SECONDS
    )
    perf_events_enabled = config["features"].get("perf_events_enabled", True)

    return ConfigResponse(
        sampling_interval_seconds=sampling_interval_seconds,
        perf_events_enabled=perf_events_enabled,
        retention_days=retention.retention_days,
        archive_enabled=retention.archive_enabled,
        downsample_after_days=retention.downsample_after_days,
        downsample_interval=retention.downsample_interval,
        app_version=settings.APP_VERSION,
    )


@router.put("", response_model=ConfigUpdateResponse)
async def update_config(
    current_user: CurrentUser,
    db: DbSession,
    payload: ConfigUpdate,
) -> ConfigUpdateResponse:
    """Update configuration values."""
    if (
        payload.retention_days is not None
        or payload.archive_enabled is not None
        or payload.downsample_after_days is not None
        or payload.downsample_interval is not None
    ):
        retention = await get_retention_policy(db)
        retention_days = payload.retention_days or retention.retention_days
        downsample_after_days = (
            payload.downsample_after_days
            if payload.downsample_after_days is not None
            else retention.downsample_after_days
        )
        downsample_interval = (
            payload.downsample_interval
            if payload.downsample_interval is not None
            else retention.downsample_interval
        )
        _validate_retention_update(retention_days, downsample_after_days, downsample_interval)
        retention = await update_retention_policy(
            db,
            retention_days=payload.retention_days,
            archive_enabled=payload.archive_enabled,
            downsample_after_days=payload.downsample_after_days,
            downsample_interval=payload.downsample_interval,
        )
    else:
        retention = await get_retention_policy(db)

    config = await update_config_values(
        db,
        sampling_interval_seconds=payload.sampling_interval_seconds,
        perf_events_enabled=payload.perf_events_enabled,
    )

    sampling_interval_seconds = config["sampling"].get(
        "interval_seconds", settings.SAMPLING_INTERVAL_SECONDS
    )
    perf_events_enabled = config["features"].get("perf_events_enabled", True)

    return ConfigUpdateResponse(
        message="Configuration updated",
        config=ConfigResponse(
            sampling_interval_seconds=sampling_interval_seconds,
            perf_events_enabled=perf_events_enabled,
            retention_days=retention.retention_days,
            archive_enabled=retention.archive_enabled,
            downsample_after_days=retention.downsample_after_days,
            downsample_interval=retention.downsample_interval,
            app_version=settings.APP_VERSION,
        ),
    )
