"""Service for application configuration stored in the database."""

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Config


DEFAULT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "sampling": {"interval_seconds": settings.SAMPLING_INTERVAL_SECONDS},
    "features": {"perf_events_enabled": True},
}


async def _get_or_create_config(session: AsyncSession, key: str) -> Config:
    result = await session.execute(select(Config).where(Config.key == key))
    config = result.scalar_one_or_none()
    if config is None:
        config = Config(key=key, value=DEFAULT_CONFIGS.get(key, {}))
        session.add(config)
        await session.commit()
        await session.refresh(config)
    return config


async def get_config_values(session: AsyncSession) -> Dict[str, Dict[str, Any]]:
    """Return config values for known keys."""
    sampling = await _get_or_create_config(session, "sampling")
    features = await _get_or_create_config(session, "features")
    return {"sampling": sampling.value, "features": features.value}


async def update_config_values(
    session: AsyncSession,
    *,
    sampling_interval_seconds: Optional[int] = None,
    perf_events_enabled: Optional[bool] = None,
) -> Dict[str, Dict[str, Any]]:
    """Update config values and return the updated configs."""
    sampling = await _get_or_create_config(session, "sampling")
    features = await _get_or_create_config(session, "features")

    if sampling_interval_seconds is not None:
        sampling.value = {
            **(sampling.value or {}),
            "interval_seconds": sampling_interval_seconds,
        }
        settings.SAMPLING_INTERVAL_SECONDS = sampling_interval_seconds

    if perf_events_enabled is not None:
        features.value = {
            **(features.value or {}),
            "perf_events_enabled": perf_events_enabled,
        }

    await session.commit()
    await session.refresh(sampling)
    await session.refresh(features)

    return {"sampling": sampling.value, "features": features.value}
