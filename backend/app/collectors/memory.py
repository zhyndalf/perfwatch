"""Memory metrics collector using psutil.

Collects RAM and swap usage statistics.
"""

from typing import Any, Dict, Optional
import logging

import psutil

from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class MemoryCollector(BaseCollector):
    """Collector for memory metrics using psutil.

    Collects:
    - Total, available, used physical memory
    - Memory usage percentage
    - Swap total, used, percentage
    - Buffers and cached (Linux only)
    """

    name = "memory"

    async def collect(self) -> Dict[str, Any]:
        """Collect memory metrics.

        Returns:
            Dictionary containing memory metrics.
        """
        # Get virtual memory stats
        mem = psutil.virtual_memory()

        result: Dict[str, Any] = {
            "total_bytes": mem.total,
            "available_bytes": mem.available,
            "used_bytes": mem.used,
            "usage_percent": mem.percent,
            # Linux-specific fields
            "buffers_bytes": getattr(mem, "buffers", None),
            "cached_bytes": getattr(mem, "cached", None),
            "shared_bytes": getattr(mem, "shared", None),
        }

        # Get swap memory stats
        swap = psutil.swap_memory()
        result.update({
            "swap_total_bytes": swap.total,
            "swap_used_bytes": swap.used,
            "swap_free_bytes": swap.free,
            "swap_percent": swap.percent,
            "swap_sin_bytes": getattr(swap, "sin", None),  # Bytes swapped in
            "swap_sout_bytes": getattr(swap, "sout", None),  # Bytes swapped out
        })

        return result
