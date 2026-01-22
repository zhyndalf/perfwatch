"""Metrics-related Pydantic schemas.

These schemas define the structure of metrics data for API responses
and database storage.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# === CPU Metrics ===

class CPUMetrics(BaseModel):
    """CPU metrics snapshot."""

    usage_percent: float = Field(..., description="Overall CPU usage percentage")
    per_core: List[float] = Field(default_factory=list, description="Per-core usage percentages")
    user: float = Field(0.0, description="Time spent in user mode")
    system: float = Field(0.0, description="Time spent in kernel mode")
    idle: float = Field(0.0, description="Time spent idle")
    iowait: Optional[float] = Field(None, description="Time waiting for I/O (Linux only)")
    frequency_mhz: Optional[List[float]] = Field(None, description="Per-core frequencies in MHz")
    temperature: Optional[float] = Field(None, description="CPU temperature in Celsius")
    load_avg: Optional[List[float]] = Field(None, description="1, 5, 15 minute load averages")


# === Memory Metrics ===

class MemoryMetrics(BaseModel):
    """Memory metrics snapshot."""

    total_bytes: int = Field(..., description="Total physical memory")
    available_bytes: int = Field(..., description="Available memory")
    used_bytes: int = Field(..., description="Used memory")
    usage_percent: float = Field(..., description="Memory usage percentage")
    swap_total_bytes: int = Field(0, description="Total swap space")
    swap_used_bytes: int = Field(0, description="Used swap space")
    swap_percent: float = Field(0.0, description="Swap usage percentage")
    buffers_bytes: Optional[int] = Field(None, description="Buffer cache (Linux)")
    cached_bytes: Optional[int] = Field(None, description="Page cache (Linux)")


# === Network Metrics ===

class NetworkInterfaceMetrics(BaseModel):
    """Metrics for a single network interface."""

    name: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int = 0
    errors_out: int = 0
    drop_in: int = 0
    drop_out: int = 0


class NetworkMetrics(BaseModel):
    """Network metrics snapshot."""

    bytes_sent_per_sec: float = Field(0.0, description="Total bytes sent per second")
    bytes_recv_per_sec: float = Field(0.0, description="Total bytes received per second")
    total_bytes_sent: int = Field(0, description="Total bytes sent since boot")
    total_bytes_recv: int = Field(0, description="Total bytes received since boot")
    interfaces: List[NetworkInterfaceMetrics] = Field(default_factory=list)
    connection_count: int = Field(0, description="Number of active connections")


# === Perf Events Metrics ===

class PerfEventsMetrics(BaseModel):
    """Hardware performance counter metrics from Linux perf_events."""

    available: bool = Field(False, description="Whether perf_events is available")
    cpu_cores: Optional[str] = Field(None, description="CPU cores targeted (or 'all')")
    interval_ms: Optional[int] = Field(None, description="perf stat interval in milliseconds")
    sample_time: Optional[str] = Field(None, description="perf stat sample timestamp")
    events: Optional[Dict[str, Any]] = Field(None, description="Perf event values")
    missing_events: Optional[List[str]] = Field(None, description="Events missing from output")
    unsupported_events: Optional[List[str]] = Field(None, description="Events not supported")


# === Memory Bandwidth Metrics ===

class MemoryBandwidthMetrics(BaseModel):
    """Memory bandwidth metrics from /proc/vmstat.

    These metrics track disk ↔ memory I/O activity (page cache operations).
    Note: This is not true CPU ↔ memory bandwidth, which requires uncore counters.
    """

    available: bool = Field(False, description="Whether metrics are available")
    # Page I/O rates (from vmstat pgpgin/pgpgout, in KB/sec)
    pgpgin_per_sec: Optional[float] = Field(None, description="Pages read from disk (KB/sec)")
    pgpgout_per_sec: Optional[float] = Field(None, description="Pages written to disk (KB/sec)")
    # Swap rates (pages/sec)
    pswpin_per_sec: Optional[float] = Field(None, description="Pages swapped in per second")
    pswpout_per_sec: Optional[float] = Field(None, description="Pages swapped out per second")
    # Aggregated metrics (bytes/sec)
    page_io_bytes_per_sec: Optional[float] = Field(None, description="Total page I/O (bytes/sec)")
    swap_io_bytes_per_sec: Optional[float] = Field(None, description="Swap I/O (bytes/sec)")
    # Page fault rates
    pgfault_per_sec: Optional[float] = Field(None, description="Page faults per second")
    pgmajfault_per_sec: Optional[float] = Field(None, description="Major page faults per second")


# === Disk Metrics ===

class DiskPartitionMetrics(BaseModel):
    """Metrics for a single disk partition."""

    device: str
    mountpoint: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    usage_percent: float


class DiskIOMetrics(BaseModel):
    """Disk I/O metrics."""

    read_bytes_per_sec: float = 0.0
    write_bytes_per_sec: float = 0.0
    read_count: int = 0
    write_count: int = 0
    read_time_ms: int = 0
    write_time_ms: int = 0


class DiskMetrics(BaseModel):
    """Disk metrics snapshot."""

    partitions: List[DiskPartitionMetrics] = Field(default_factory=list)
    io: DiskIOMetrics = Field(default_factory=DiskIOMetrics)


# === Aggregated Snapshot ===

class MetricsSnapshot(BaseModel):
    """Combined snapshot from all collectors.

    This is the main schema for real-time WebSocket data and historical storage.
    """

    timestamp: datetime = Field(..., description="Collection timestamp (UTC)")
    cpu: Optional[Dict[str, Any]] = Field(None, description="CPU metrics")
    memory: Optional[Dict[str, Any]] = Field(None, description="Memory metrics")
    network: Optional[Dict[str, Any]] = Field(None, description="Network metrics")
    disk: Optional[Dict[str, Any]] = Field(None, description="Disk metrics")
    perf_events: Optional[Dict[str, Any]] = Field(None, description="Hardware perf counters")
    memory_bandwidth: Optional[Dict[str, Any]] = Field(None, description="Memory I/O bandwidth")

    model_config = ConfigDict(from_attributes=True)


class MetricsHistoryQuery(BaseModel):
    """Query parameters for historical metrics."""

    start_time: datetime = Field(..., description="Start of time range")
    end_time: datetime = Field(..., description="End of time range")
    metric_type: Optional[str] = Field(None, description="Filter by metric type")
    interval: Optional[int] = Field(None, description="Downsample interval in seconds")
    limit: int = Field(default=1000, ge=1, le=10000, description="Maximum results to return")


class MetricsHistoryResponse(BaseModel):
    """Response for historical metrics query."""

    count: int = Field(..., description="Number of snapshots returned")
    start_time: datetime
    end_time: datetime
    snapshots: List[MetricsSnapshot] = Field(default_factory=list)
