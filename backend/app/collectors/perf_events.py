"""Linux perf_events collector for hardware performance counters.

Uses ctypes to directly call the perf_event_open syscall for collecting
CPU cycles and instructions, enabling IPC (Instructions Per Cycle) calculation.

This collector gracefully degrades when perf_events is unavailable (e.g.,
in containers without proper privileges or on systems without perf support).
"""

import ctypes
import ctypes.util
import errno
import logging
import os
from typing import Any, Dict, List, Optional

from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

# Syscall number for perf_event_open (architecture-dependent)
# x86_64: 298, aarch64: 241
_SYSCALL_PERF_EVENT_OPEN = {
    "x86_64": 298,
    "aarch64": 241,
    "arm": 364,
}

# perf_event_open constants from linux/perf_event.h
PERF_TYPE_HARDWARE = 0
PERF_TYPE_HW_CACHE = 3

# Hardware event types
PERF_COUNT_HW_CPU_CYCLES = 0
PERF_COUNT_HW_INSTRUCTIONS = 1

# Hardware cache event IDs (perf_hw_cache_id)
PERF_COUNT_HW_CACHE_L1D = 0   # L1 Data cache
PERF_COUNT_HW_CACHE_L1I = 1   # L1 Instruction cache
PERF_COUNT_HW_CACHE_LL = 2    # Last Level Cache (L3 or L2 depending on CPU)
PERF_COUNT_HW_CACHE_DTLB = 3  # Data TLB
PERF_COUNT_HW_CACHE_ITLB = 4  # Instruction TLB
PERF_COUNT_HW_CACHE_BPU = 5   # Branch Prediction Unit

# Hardware cache operation IDs (perf_hw_cache_op_id)
PERF_COUNT_HW_CACHE_OP_READ = 0
PERF_COUNT_HW_CACHE_OP_WRITE = 1
PERF_COUNT_HW_CACHE_OP_PREFETCH = 2

# Hardware cache operation result IDs (perf_hw_cache_op_result_id)
PERF_COUNT_HW_CACHE_RESULT_ACCESS = 0
PERF_COUNT_HW_CACHE_RESULT_MISS = 1

# perf_event_open flags
PERF_FLAG_FD_CLOEXEC = 8


def encode_cache_config(cache_id: int, op_id: int, result_id: int) -> int:
    """Encode a hardware cache event configuration.

    Cache events use a 64-bit config encoded as:
    config = cache_id | (op_id << 8) | (result_id << 16)

    Args:
        cache_id: Cache level (L1D, L1I, LL, etc.)
        op_id: Operation type (READ, WRITE, PREFETCH)
        result_id: Result type (ACCESS, MISS)

    Returns:
        Encoded config value for perf_event_open
    """
    return cache_id | (op_id << 8) | (result_id << 16)


# Pre-computed cache event configs
CACHE_L1D_READ_ACCESS = encode_cache_config(
    PERF_COUNT_HW_CACHE_L1D,
    PERF_COUNT_HW_CACHE_OP_READ,
    PERF_COUNT_HW_CACHE_RESULT_ACCESS
)
CACHE_L1D_READ_MISS = encode_cache_config(
    PERF_COUNT_HW_CACHE_L1D,
    PERF_COUNT_HW_CACHE_OP_READ,
    PERF_COUNT_HW_CACHE_RESULT_MISS
)
CACHE_LL_READ_ACCESS = encode_cache_config(
    PERF_COUNT_HW_CACHE_LL,
    PERF_COUNT_HW_CACHE_OP_READ,
    PERF_COUNT_HW_CACHE_RESULT_ACCESS
)
CACHE_LL_READ_MISS = encode_cache_config(
    PERF_COUNT_HW_CACHE_LL,
    PERF_COUNT_HW_CACHE_OP_READ,
    PERF_COUNT_HW_CACHE_RESULT_MISS
)


class PerfEventAttr(ctypes.Structure):
    """Structure matching struct perf_event_attr from linux/perf_event.h.

    This is a simplified version with only the fields we need.
    The full structure is much larger, but the kernel only reads
    up to the 'size' field we specify.
    """

    _fields_ = [
        ("type", ctypes.c_uint32),          # Type of event
        ("size", ctypes.c_uint32),          # Size of this structure
        ("config", ctypes.c_uint64),        # Type-specific configuration
        ("sample_period", ctypes.c_uint64),  # Period or frequency
        ("sample_type", ctypes.c_uint64),   # What data to record
        ("read_format", ctypes.c_uint64),   # How to read data
        ("flags", ctypes.c_uint64),         # Flags (disabled, inherit, etc.)
        # Padding to match kernel structure size (at least 80 bytes for basic ops)
        ("_pad1", ctypes.c_uint64),
        ("_pad2", ctypes.c_uint64),
        ("_pad3", ctypes.c_uint64),
        ("_pad4", ctypes.c_uint64),
        ("_pad5", ctypes.c_uint64),
    ]


def _get_arch() -> str:
    """Get the current architecture for syscall number lookup."""
    import platform
    machine = platform.machine()
    if machine in ("x86_64", "AMD64"):
        return "x86_64"
    elif machine in ("aarch64", "arm64"):
        return "aarch64"
    elif machine.startswith("arm"):
        return "arm"
    return machine


def _get_libc():
    """Get libc for syscall access."""
    libc_name = ctypes.util.find_library("c")
    if libc_name:
        return ctypes.CDLL(libc_name, use_errno=True)
    # Fallback to direct loading
    return ctypes.CDLL("libc.so.6", use_errno=True)


class PerfEventsCollector(BaseCollector):
    """Collector for Linux perf_events hardware counters.

    Collects:
    - CPU cycles count
    - Instructions count
    - IPC (Instructions Per Cycle)
    - L1 data cache references and misses
    - LLC (Last Level Cache) references and misses
    - Cache miss rates

    This collector uses the Linux perf_events interface via ctypes
    to read hardware performance counters without external dependencies.

    When perf_events is unavailable (unprivileged container, missing
    kernel support, or restricted by perf_event_paranoid), the collector
    gracefully returns {"available": False}.

    Attributes:
        name: Collector identifier ('perf_events')
        enabled: Whether the collector is active
    """

    name = "perf_events"

    def __init__(self, enabled: bool = True):
        """Initialize the perf events collector.

        Args:
            enabled: Whether this collector should be active
        """
        super().__init__(enabled=enabled)
        self._available: Optional[bool] = None
        self._fds: Dict[str, int] = {}  # event_name -> file descriptor
        self._libc = None
        self._syscall_nr: Optional[int] = None
        self._initialized = False

    def _initialize(self) -> bool:
        """Initialize the perf_events infrastructure.

        Returns:
            True if initialization successful, False otherwise.
        """
        if self._initialized:
            return self._available or False

        self._initialized = True

        try:
            # Get architecture-specific syscall number
            arch = _get_arch()
            self._syscall_nr = _SYSCALL_PERF_EVENT_OPEN.get(arch)

            if self._syscall_nr is None:
                logger.debug(f"perf_events: Unsupported architecture: {arch}")
                self._available = False
                return False

            # Get libc for syscall
            self._libc = _get_libc()

            # Check if perf_events is available
            if not self._check_paranoid():
                self._available = False
                return False

            # Try to open events
            if not self._open_events():
                self._available = False
                return False

            self._available = True
            return True

        except Exception as e:
            logger.debug(f"perf_events: Initialization failed: {e}")
            self._available = False
            return False

    def _check_paranoid(self) -> bool:
        """Check if perf_events is potentially available via paranoid setting.

        Returns:
            True if perf_events might be available, False otherwise.
        """
        paranoid_path = "/proc/sys/kernel/perf_event_paranoid"

        try:
            if not os.path.exists(paranoid_path):
                logger.debug("perf_events: /proc/sys/kernel/perf_event_paranoid not found")
                return False

            with open(paranoid_path, "r") as f:
                paranoid_value = int(f.read().strip())

            # paranoid values:
            # -1: Allow all users
            #  0: Allow non-root users to read kernel-level data
            #  1: Allow non-root users to read user-level data (default on many systems)
            #  2: Only root can use perf
            #  3: No perf_events at all (some hardened systems)
            logger.debug(f"perf_events: paranoid level = {paranoid_value}")

            # We need level 2 or lower for basic hardware counters
            # But the actual permission also depends on capabilities
            # So we'll try the syscall regardless and handle EPERM
            return True

        except Exception as e:
            logger.debug(f"perf_events: Failed to check paranoid: {e}")
            return False

    def _perf_event_open(
        self,
        event_type: int,
        event_config: int,
        pid: int = 0,
        cpu: int = -1,
        group_fd: int = -1,
        flags: int = PERF_FLAG_FD_CLOEXEC,
    ) -> int:
        """Call the perf_event_open syscall.

        Args:
            event_type: Type of event (PERF_TYPE_HARDWARE, etc.)
            event_config: Event-specific configuration
            pid: Process ID (0 = current process, -1 = all processes)
            cpu: CPU to monitor (-1 = any CPU)
            group_fd: File descriptor of group leader (-1 = new group)
            flags: Flags for the syscall

        Returns:
            File descriptor on success, -1 on failure.
        """
        attr = PerfEventAttr()
        attr.type = event_type
        attr.size = ctypes.sizeof(PerfEventAttr)
        attr.config = event_config
        attr.flags = 0  # We're not setting disabled bit, etc.

        # Call syscall directly
        fd = self._libc.syscall(
            self._syscall_nr,
            ctypes.byref(attr),
            pid,
            cpu,
            group_fd,
            flags,
        )

        if fd < 0:
            err = ctypes.get_errno()
            logger.debug(
                f"perf_event_open failed: errno={err} ({errno.errorcode.get(err, 'UNKNOWN')})"
            )

        return fd

    def _open_events(self) -> bool:
        """Open file descriptors for the events we want to monitor.

        Returns:
            True if at least one event was successfully opened.
        """
        # Hardware events (cycles, instructions)
        hw_events = {
            "cycles": PERF_COUNT_HW_CPU_CYCLES,
            "instructions": PERF_COUNT_HW_INSTRUCTIONS,
        }

        for name, config in hw_events.items():
            fd = self._perf_event_open(PERF_TYPE_HARDWARE, config)
            if fd >= 0:
                self._fds[name] = fd
                logger.debug(f"perf_events: Opened {name} counter (fd={fd})")
            else:
                logger.debug(f"perf_events: Failed to open {name} counter")

        # Cache events (L1D and LLC)
        cache_events = {
            "l1d_references": CACHE_L1D_READ_ACCESS,
            "l1d_misses": CACHE_L1D_READ_MISS,
            "llc_references": CACHE_LL_READ_ACCESS,
            "llc_misses": CACHE_LL_READ_MISS,
        }

        for name, config in cache_events.items():
            fd = self._perf_event_open(PERF_TYPE_HW_CACHE, config)
            if fd >= 0:
                self._fds[name] = fd
                logger.debug(f"perf_events: Opened {name} counter (fd={fd})")
            else:
                logger.debug(f"perf_events: Failed to open {name} counter")

        return len(self._fds) > 0

    def _read_counter(self, fd: int) -> Optional[int]:
        """Read a counter value from a file descriptor.

        Args:
            fd: File descriptor from perf_event_open

        Returns:
            Counter value, or None on error.
        """
        try:
            # Read 8 bytes (uint64_t counter value)
            data = os.read(fd, 8)
            if len(data) == 8:
                return int.from_bytes(data, byteorder="little", signed=False)
            return None
        except Exception as e:
            logger.debug(f"perf_events: Failed to read counter: {e}")
            return None

    def is_available(self) -> bool:
        """Check if perf_events is available on this system.

        Returns:
            True if perf_events can be used, False otherwise.
        """
        if self._available is None:
            self._initialize()
        return self._available or False

    async def collect(self) -> Dict[str, Any]:
        """Collect hardware performance counters.

        Returns:
            Dictionary containing:
            - available: bool - Whether perf_events is available
            - cycles: int - CPU cycles count (if available)
            - instructions: int - Instructions count (if available)
            - ipc: float - Instructions Per Cycle (if available)
            - l1d_references: int - L1 data cache accesses (if available)
            - l1d_misses: int - L1 data cache misses (if available)
            - l1d_miss_rate: float - L1 miss rate (if available)
            - llc_references: int - LLC accesses (if available)
            - llc_misses: int - LLC misses (if available)
            - llc_miss_rate: float - LLC miss rate (if available)
        """
        # Check availability (will initialize if needed)
        if not self.is_available():
            return {"available": False}

        # Read hardware counters
        cycles = None
        instructions = None

        if "cycles" in self._fds:
            cycles = self._read_counter(self._fds["cycles"])

        if "instructions" in self._fds:
            instructions = self._read_counter(self._fds["instructions"])

        # Calculate IPC
        ipc = None
        if cycles is not None and instructions is not None and cycles > 0:
            ipc = instructions / cycles

        # Read cache counters
        l1d_references = None
        l1d_misses = None
        llc_references = None
        llc_misses = None

        if "l1d_references" in self._fds:
            l1d_references = self._read_counter(self._fds["l1d_references"])

        if "l1d_misses" in self._fds:
            l1d_misses = self._read_counter(self._fds["l1d_misses"])

        if "llc_references" in self._fds:
            llc_references = self._read_counter(self._fds["llc_references"])

        if "llc_misses" in self._fds:
            llc_misses = self._read_counter(self._fds["llc_misses"])

        # Calculate cache miss rates
        l1d_miss_rate = None
        if l1d_references is not None and l1d_misses is not None and l1d_references > 0:
            l1d_miss_rate = l1d_misses / l1d_references

        llc_miss_rate = None
        if llc_references is not None and llc_misses is not None and llc_references > 0:
            llc_miss_rate = llc_misses / llc_references

        return {
            "available": True,
            # CPU counters
            "cycles": cycles,
            "instructions": instructions,
            "ipc": ipc,
            # L1 data cache
            "l1d_references": l1d_references,
            "l1d_misses": l1d_misses,
            "l1d_miss_rate": l1d_miss_rate,
            # Last Level Cache
            "llc_references": llc_references,
            "llc_misses": llc_misses,
            "llc_miss_rate": llc_miss_rate,
        }

    def close(self) -> None:
        """Close all open file descriptors."""
        for name, fd in self._fds.items():
            try:
                os.close(fd)
                logger.debug(f"perf_events: Closed {name} counter (fd={fd})")
            except Exception as e:
                logger.debug(f"perf_events: Failed to close {name}: {e}")
        self._fds.clear()
        self._available = None
        self._initialized = False

    def __del__(self):
        """Clean up file descriptors on deletion."""
        # Only close if we have real file descriptors (not mocked values in tests)
        if hasattr(self, '_fds') and self._fds:
            self.close()
