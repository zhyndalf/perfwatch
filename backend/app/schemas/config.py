"""Schemas for application configuration settings."""

from pydantic import BaseModel, Field
from typing import Optional


class ConfigResponse(BaseModel):
    sampling_interval_seconds: int = Field(..., ge=1)
    perf_events_enabled: bool
    retention_days: int = Field(..., ge=1)
    archive_enabled: bool
    downsample_after_days: int = Field(..., ge=0)
    downsample_interval: str
    app_version: str


class ConfigUpdate(BaseModel):
    sampling_interval_seconds: Optional[int] = Field(None, ge=1)
    perf_events_enabled: Optional[bool] = None
    retention_days: Optional[int] = Field(None, ge=1)
    archive_enabled: Optional[bool] = None
    downsample_after_days: Optional[int] = Field(None, ge=0)
    downsample_interval: Optional[str] = None


class ConfigUpdateResponse(BaseModel):
    message: str
    config: ConfigResponse
