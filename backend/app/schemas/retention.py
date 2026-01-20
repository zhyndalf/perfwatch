"""Schemas for data retention policy settings."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RetentionPolicyBase(BaseModel):
    """Base schema for retention policy settings."""

    retention_days: int = Field(..., ge=1, description="Days to retain metrics data")
    archive_enabled: bool = Field(True, description="Whether retention cleanup is enabled")
    downsample_after_days: int = Field(
        7, ge=0, description="Days after which downsampling should apply"
    )
    downsample_interval: str = Field(
        "1h", description="Downsample interval: 5s, 1m, 5m, 1h"
    )


class RetentionPolicyUpdate(BaseModel):
    """Update payload for retention policy settings."""

    retention_days: Optional[int] = Field(None, ge=1)
    archive_enabled: Optional[bool] = None
    downsample_after_days: Optional[int] = Field(None, ge=0)
    downsample_interval: Optional[str] = None


class RetentionPolicyResponse(RetentionPolicyBase):
    """Response schema for retention policy settings."""

    id: int
    last_archive_run: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RetentionCleanupResponse(BaseModel):
    """Response schema for retention cleanup runs."""

    deleted_count: int
    downsampled_count: int
    last_archive_run: Optional[datetime] = None
