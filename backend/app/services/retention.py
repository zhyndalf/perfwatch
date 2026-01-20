"""Retention policy service for historical metrics cleanup."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArchivePolicy
from app.models.metrics import MetricsSnapshot


DEFAULT_RETENTION = {
    "retention_days": 30,
    "archive_enabled": True,
    "downsample_after_days": 7,
    "downsample_interval": "1h",
}


async def get_retention_policy(session: AsyncSession) -> ArchivePolicy:
    """Return the single retention policy, creating defaults if missing."""
    result = await session.execute(select(ArchivePolicy))
    policy = result.scalar_one_or_none()
    if policy is None:
        policy = ArchivePolicy(**DEFAULT_RETENTION)
        session.add(policy)
        await session.commit()
        await session.refresh(policy)
    return policy


async def update_retention_policy(
    session: AsyncSession,
    *,
    retention_days: Optional[int] = None,
    archive_enabled: Optional[bool] = None,
    downsample_after_days: Optional[int] = None,
    downsample_interval: Optional[str] = None,
) -> ArchivePolicy:
    """Update retention policy settings and return the updated model."""
    policy = await get_retention_policy(session)

    if retention_days is not None:
        policy.retention_days = retention_days
    if archive_enabled is not None:
        policy.archive_enabled = archive_enabled
    if downsample_after_days is not None:
        policy.downsample_after_days = downsample_after_days
    if downsample_interval is not None:
        policy.downsample_interval = downsample_interval

    await session.commit()
    await session.refresh(policy)
    return policy


async def cleanup_expired_metrics(
    session: AsyncSession,
    *,
    now: Optional[datetime] = None,
) -> int:
    """Delete metrics snapshots older than the retention cutoff."""
    policy = await get_retention_policy(session)
    if not policy.archive_enabled:
        return 0

    if now is None:
        now = datetime.now(timezone.utc)

    cutoff = now - timedelta(days=policy.retention_days)
    count_result = await session.execute(
        select(func.count())
        .select_from(MetricsSnapshot)
        .where(MetricsSnapshot.timestamp < cutoff)
    )
    delete_count = int(count_result.scalar_one() or 0)
    await session.execute(
        delete(MetricsSnapshot).where(MetricsSnapshot.timestamp < cutoff)
    )
    policy.last_archive_run = now
    await session.commit()
    return delete_count


async def apply_retention_policy(
    session: AsyncSession,
    *,
    now: Optional[datetime] = None,
) -> Tuple[int, int]:
    """Apply retention cleanup and return (deleted_count, downsampled_count)."""
    deleted = await cleanup_expired_metrics(session, now=now)
    downsampled = 0
    return deleted, downsampled
