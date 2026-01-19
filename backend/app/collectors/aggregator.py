"""Metrics aggregator for coordinating multiple collectors.

The aggregator manages a collection of metric collectors and provides
methods for collecting from all of them simultaneously.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
import logging

from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class MetricsAggregator:
    """Coordinates metric collection from multiple collectors.

    The aggregator can collect from all registered collectors at once,
    or run periodic collection with a callback for each snapshot.

    Attributes:
        collectors: List of registered collectors
        interval: Collection interval in seconds (default 5.0)
    """

    def __init__(
        self,
        collectors: Optional[List[BaseCollector]] = None,
        interval: float = 5.0,
    ):
        """Initialize the aggregator.

        Args:
            collectors: List of collectors to use (can add more later)
            interval: Seconds between collections when running periodically
        """
        self.collectors: List[BaseCollector] = collectors or []
        self.interval = interval
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def add_collector(self, collector: BaseCollector) -> None:
        """Add a collector to the aggregator.

        Args:
            collector: The collector to add
        """
        self.collectors.append(collector)
        logger.info(f"Added collector: {collector.name}")

    def remove_collector(self, name: str) -> bool:
        """Remove a collector by name.

        Args:
            name: Name of the collector to remove

        Returns:
            True if collector was found and removed, False otherwise
        """
        for i, collector in enumerate(self.collectors):
            if collector.name == name:
                del self.collectors[i]
                logger.info(f"Removed collector: {name}")
                return True
        return False

    def get_collector(self, name: str) -> Optional[BaseCollector]:
        """Get a collector by name.

        Args:
            name: Name of the collector to find

        Returns:
            The collector if found, None otherwise
        """
        for collector in self.collectors:
            if collector.name == name:
                return collector
        return None

    async def collect_all(self) -> Dict[str, Any]:
        """Collect from all collectors and combine results.

        Runs all collectors concurrently and combines their results
        into a single dictionary keyed by collector name.

        Returns:
            Dictionary with collector names as keys and their data as values,
            plus a top-level timestamp.
        """
        timestamp = datetime.now(timezone.utc)

        # Collect from all collectors concurrently
        tasks = [collector.safe_collect() for collector in self.collectors]
        results = await asyncio.gather(*tasks)

        # Build the aggregated snapshot
        snapshot: Dict[str, Any] = {
            "timestamp": timestamp.isoformat(),
        }

        for collector, data in zip(self.collectors, results):
            snapshot[collector.name] = data

        return snapshot

    async def start(
        self,
        callback: Callable[[Dict[str, Any]], Any],
    ) -> None:
        """Start periodic collection with callback for each snapshot.

        This method runs indefinitely until stop() is called. Each interval,
        it collects from all collectors and calls the callback with the
        aggregated snapshot.

        Args:
            callback: Async or sync function to call with each snapshot
        """
        if self._running:
            logger.warning("Aggregator is already running")
            return

        self._running = True
        logger.info(f"Starting aggregator with {self.interval}s interval")

        while self._running:
            try:
                snapshot = await self.collect_all()

                # Support both async and sync callbacks
                if asyncio.iscoroutinefunction(callback):
                    await callback(snapshot)
                else:
                    callback(snapshot)

            except Exception as e:
                logger.error(f"Error in collection cycle: {e}")

            # Wait for next interval
            await asyncio.sleep(self.interval)

        logger.info("Aggregator stopped")

    def stop(self) -> None:
        """Stop periodic collection.

        If the aggregator is running via start(), this will cause it
        to exit after the current collection cycle completes.
        """
        self._running = False
        logger.info("Aggregator stop requested")

    @property
    def is_running(self) -> bool:
        """Check if the aggregator is currently running."""
        return self._running

    @property
    def collector_names(self) -> List[str]:
        """Get list of registered collector names."""
        return [c.name for c in self.collectors]

    def __repr__(self) -> str:
        names = ", ".join(self.collector_names)
        return f"<MetricsAggregator(collectors=[{names}], interval={self.interval})>"
