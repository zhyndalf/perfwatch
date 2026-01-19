"""Configuration model for application settings."""

from datetime import datetime
from typing import Any
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database import Base


class Config(Base):
    """
    Key-value store for application configuration.

    Default keys:
    - sampling: {"interval_seconds": 5}
    - retention: {"days": 30, "archive_enabled": true, ...}
    - features: {"perf_events_enabled": true}
    """

    __tablename__ = "config"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Config(key={self.key})>"
