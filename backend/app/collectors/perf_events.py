"""Perf stat-based collector for hardware performance counters.

This collector uses `perf stat -I` to stream counter values at a fixed interval.
It parses perf's CSV output and returns the latest interval snapshot.
"""

import asyncio
import logging
import os
import re
import shutil
from typing import Any, Dict, Optional, Tuple

from app.collectors.base import BaseCollector
from app.config import settings

logger = logging.getLogger(__name__)

PERF_STAT_EVENTS = [
    "cpu-clock",
    "context-switches",
    "cpu-migrations",
    "page-faults",
    "cycles",
    "instructions",
    "branches",
    "branch-misses",
    "L1-dcache-loads",
    "L1-dcache-load-misses",
    "LLC-loads",
    "LLC-load-misses",
    "L1-icache-loads",
    "dTLB-loads",
    "dTLB-load-misses",
    "iTLB-loads",
    "iTLB-load-misses",
]

_UNSUPPORTED_VALUES = {"<not supported>", "<not counted>"}
_CPU_LIST_PATTERN = re.compile(r"^(all|\d+([,-]\d+)*)$")


def normalize_cpu_list(value: Optional[str]) -> Optional[str]:
    """Normalize CPU core list for perf stat.

    Returns None for "all" or empty values.
    """
    if value is None:
        return None
    trimmed = value.strip()
    if not trimmed or trimmed.lower() == "all":
        return None
    return trimmed


def parse_perf_stat_line(line: str) -> Optional[Tuple[str, str, Optional[float], Optional[str], bool]]:
    """Parse a single perf stat CSV line.

    Returns:
        Tuple of (time, event, value, unit, supported)
    """
    if not line:
        return None

    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 4:
        return None

    time_value = parts[0]
    raw_value = parts[1]
    unit = parts[2] or None
    event = parts[3]

    if event not in PERF_STAT_EVENTS:
        return None

    if raw_value in _UNSUPPORTED_VALUES:
        return time_value, event, None, unit, False

    try:
        if "." in raw_value or "e" in raw_value or "E" in raw_value:
            value = float(raw_value)
        else:
            value = int(raw_value)
    except ValueError:
        return time_value, event, None, unit, False

    return time_value, event, value, unit, True


class PerfEventsCollector(BaseCollector):
    """Collector using perf stat for hardware performance counters."""

    name = "perf_events"

    def __init__(self, enabled: bool = True):
        super().__init__(enabled=enabled)
        self._proc: Optional[asyncio.subprocess.Process] = None
        self._reader_task: Optional[asyncio.Task] = None
        self._latest: Optional[Dict[str, Any]] = None
        self._available: Optional[bool] = None
        self._last_error: Optional[str] = None
        self._unsupported_events: set[str] = set()
        self._current_time: Optional[str] = None
        self._current_events: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._start_lock = asyncio.Lock()
        self._config_signature: Optional[Tuple[Optional[str], int]] = None

    def _get_config(self) -> Tuple[Optional[str], int]:
        cpu_cores = normalize_cpu_list(getattr(settings, "PERF_EVENTS_CPU_CORES", None))
        interval_ms = int(getattr(settings, "PERF_EVENTS_INTERVAL_MS", 1000))
        return cpu_cores, interval_ms

    def _build_command(self, cpu_cores: Optional[str], interval_ms: int) -> list[str]:
        cmd = [
            "perf",
            "stat",
            "-ddd",
            "-I",
            str(interval_ms),
            "-x",
            ",",
            "--no-big-num",
            "--log-fd",
            "1",
            "-a",
            "-e",
            ",".join(PERF_STAT_EVENTS),
        ]
        if cpu_cores is not None:
            cmd.extend(["-C", cpu_cores])
        return cmd

    async def _start_process(self, cpu_cores: Optional[str], interval_ms: int) -> None:
        if shutil.which("perf") is None:
            self._available = False
            self._last_error = "perf binary not found"
            return

        env = os.environ.copy()
        env["LC_ALL"] = "C"

        cmd = self._build_command(cpu_cores, interval_ms)
        try:
            self._proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
            )
        except FileNotFoundError:
            self._available = False
            self._last_error = "perf binary not found"
            return
        except Exception as exc:
            self._available = False
            self._last_error = f"failed to start perf stat: {exc}"
            return

        self._available = True
        self._unsupported_events = set()
        self._current_time = None
        self._current_events = {}
        self._reader_task = asyncio.create_task(self._read_loop())

    async def _stop_process(self) -> None:
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None

        if self._proc is not None:
            if self._proc.returncode is None:
                self._proc.terminate()
                try:
                    await asyncio.wait_for(self._proc.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    self._proc.kill()
            self._proc = None

    async def _ensure_process(self, cpu_cores: Optional[str], interval_ms: int) -> None:
        async with self._start_lock:
            if self._proc is not None and self._proc.returncode is None:
                return
            await self._stop_process()
            await self._start_process(cpu_cores, interval_ms)

    async def _read_loop(self) -> None:
        assert self._proc is not None
        assert self._proc.stdout is not None

        while True:
            line = await self._proc.stdout.readline()
            if not line:
                break

            try:
                decoded = line.decode("utf-8", errors="ignore")
            except Exception:
                continue

            parsed = parse_perf_stat_line(decoded)
            if parsed is None:
                continue

            time_value, event, value, unit, supported = parsed

            if self._current_time is None:
                self._current_time = time_value

            if time_value != self._current_time:
                await self._finalize_sample()
                self._current_time = time_value
                self._current_events = {}

            if not supported:
                self._unsupported_events.add(event)

            self._current_events[event] = {
                "value": value,
                "unit": unit,
            }

        await self._finalize_sample()
        if self._available:
            self._available = False
            self._last_error = "perf stat stopped"

    async def _finalize_sample(self) -> None:
        if not self._current_time or not self._current_events:
            return

        cpu_cores, interval_ms = self._get_config()
        missing = [event for event in PERF_STAT_EVENTS if event not in self._current_events]

        events = dict(self._current_events)
        for event in missing:
            events[event] = {"value": None, "unit": None}

        available = not missing and not self._unsupported_events
        payload = {
            "available": available,
            "cpu_cores": cpu_cores or "all",
            "interval_ms": interval_ms,
            "sample_time": self._current_time,
            "events": events,
        }

        if missing:
            payload["missing_events"] = missing
        if self._unsupported_events:
            payload["unsupported_events"] = sorted(self._unsupported_events)

        async with self._lock:
            self._latest = payload
            self._available = available

    async def collect(self) -> Dict[str, Any]:
        if not getattr(settings, "PERF_EVENTS_ENABLED", True):
            await self._stop_process()
            return {
                "available": False,
                "disabled": True,
            }

        cpu_cores, interval_ms = self._get_config()
        config_signature = (cpu_cores, interval_ms)

        if self._config_signature != config_signature:
            self._config_signature = config_signature
            await self._stop_process()

        await self._ensure_process(cpu_cores, interval_ms)

        if self._available is False:
            async with self._lock:
                if self._latest is not None:
                    payload = dict(self._latest)
                    if self._last_error and "error" not in payload:
                        payload["error"] = self._last_error
                    return payload
            return {
                "available": False,
                "cpu_cores": cpu_cores or "all",
                "interval_ms": interval_ms,
                "error": self._last_error,
                "unsupported_events": sorted(self._unsupported_events),
            }

        async with self._lock:
            if self._latest is None:
                return {
                    "available": True,
                    "cpu_cores": cpu_cores or "all",
                    "interval_ms": interval_ms,
                    "events": {},
                }
            return dict(self._latest)

    async def close(self) -> None:
        await self._stop_process()
        self._latest = None
        self._available = None
        self._last_error = None
        self._unsupported_events = set()
        self._current_time = None
        self._current_events = {}
        self._config_signature = None
