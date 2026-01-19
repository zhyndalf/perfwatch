"""Metrics models for storing time-series performance data."""

from datetime import datetime
from typing import Any
from sqlalchemy import BigInteger, String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class MetricsSnapshot(Base):
    """
    Stores all collected metrics as JSONB for flexibility.

    Metric types:
    - cpu: CPU usage, per-core, frequencies, temperatures
    - memory: RAM usage, swap, buffers, caches
    - network: Interface stats, connections
    - disk: I/O stats, partition usage
    - perf: perf_events data (cache misses, IPC, etc.)
    """

    __tablename__ = "metrics_snapshot"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        Index("idx_metrics_type_timestamp", "metric_type", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<MetricsSnapshot(id={self.id}, type={self.metric_type}, timestamp={self.timestamp})>"
