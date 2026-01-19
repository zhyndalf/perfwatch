"""Base collector abstract class.

All metric collectors inherit from BaseCollector and implement the collect() method.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Abstract base class for all metric collectors.

    Subclasses must implement the `collect()` method to gather specific metrics.
    The `safe_collect()` method wraps `collect()` with error handling.

    Attributes:
        name: Unique identifier for the collector (e.g., 'cpu', 'memory')
        enabled: Whether the collector is active
    """

    name: str = "base"
    enabled: bool = True

    def __init__(self, enabled: bool = True):
        """Initialize the collector.

        Args:
            enabled: Whether this collector should be active
        """
        self.enabled = enabled

    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """Collect metrics and return as dictionary.

        Returns:
            Dictionary containing collected metrics.

        Raises:
            Exception: If collection fails (handled by safe_collect)
        """
        pass

    async def safe_collect(self) -> Dict[str, Any]:
        """Collect metrics with error handling.

        Always returns a dictionary, even on failure. On success, adds
        a timestamp. On failure, returns error information.

        Returns:
            Dictionary with metrics data and timestamp, or error info.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        if not self.enabled:
            return {
                "_enabled": False,
                "_timestamp": timestamp,
            }

        try:
            data = await self.collect()
            data["_timestamp"] = timestamp
            data["_error"] = None
            return data
        except Exception as e:
            logger.warning(f"Collector '{self.name}' failed: {e}")
            return {
                "_error": str(e),
                "_timestamp": timestamp,
            }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, enabled={self.enabled})>"
