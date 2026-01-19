"""Archive policy model for data retention settings."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class ArchivePolicy(Base):
    """
    Data retention policy settings.

    Controls how long metrics data is kept and when it's downsampled.
    """

    __tablename__ = "archive_policy"

    id: Mapped[int] = mapped_column(primary_key=True)
    retention_days: Mapped[int] = mapped_column(Integer, default=30)
    archive_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    downsample_after_days: Mapped[int] = mapped_column(Integer, default=7)
    downsample_interval: Mapped[str] = mapped_column(String(20), default="1 hour")
    last_archive_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<ArchivePolicy(id={self.id}, retention_days={self.retention_days})>"
