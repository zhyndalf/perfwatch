"""Schemas for application configuration settings."""

from pydantic import BaseModel, Field
from typing import Optional


class ConfigResponse(BaseModel):
    sampling_interval_seconds: int = Field(..., ge=1)
    perf_events_enabled: bool
    perf_events_cpu_cores: str
    perf_events_interval_ms: int = Field(..., ge=100)
    retention_days: int = Field(..., ge=1)
    archive_enabled: bool
    downsample_after_days: int = Field(..., ge=0)
    downsample_interval: str
    app_version: str


class ConfigUpdate(BaseModel):
    sampling_interval_seconds: Optional[int] = Field(None, ge=1)
    perf_events_enabled: Optional[bool] = None
    perf_events_cpu_cores: Optional[str] = Field(
        None,
        pattern=r"(?i)^(all|\\d+([,-]\\d+)*)$",
    )
    perf_events_interval_ms: Optional[int] = Field(None, ge=100)
    retention_days: Optional[int] = Field(None, ge=1)
    archive_enabled: Optional[bool] = None
    downsample_after_days: Optional[int] = Field(None, ge=0)
    downsample_interval: Optional[str] = None


class ConfigUpdateResponse(BaseModel):
    message: str
    config: ConfigResponse
