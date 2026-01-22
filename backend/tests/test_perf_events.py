"""Tests for the perf stat-based perf_events collector."""

import pytest

from app.collectors.perf_events import (
    PERF_STAT_EVENTS,
    PerfEventsCollector,
    normalize_cpu_list,
    parse_perf_stat_line,
)
from app.config import settings


def test_perf_stat_events_list():
    assert PERF_STAT_EVENTS == [
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


def test_normalize_cpu_list():
    assert normalize_cpu_list(None) is None
    assert normalize_cpu_list("") is None
    assert normalize_cpu_list("all") is None
    assert normalize_cpu_list("ALL") is None
    assert normalize_cpu_list("0-3") == "0-3"


def test_parse_perf_stat_line_numeric():
    line = "1.000000000,12345,,cycles,1000,1000"
    parsed = parse_perf_stat_line(line)
    assert parsed is not None
    time_value, event, value, unit, supported = parsed
    assert time_value == "1.000000000"
    assert event == "cycles"
    assert value == 12345
    assert unit is None
    assert supported is True


def test_parse_perf_stat_line_unsupported():
    line = "1.000000000,<not supported>,,cycles,1000,1000"
    parsed = parse_perf_stat_line(line)
    assert parsed is not None
    time_value, event, value, unit, supported = parsed
    assert time_value == "1.000000000"
    assert event == "cycles"
    assert value is None
    assert supported is False


def test_parse_perf_stat_line_ignored_event():
    line = "1.000000000,123,,unknown-event,1000,1000"
    assert parse_perf_stat_line(line) is None


@pytest.mark.asyncio
async def test_collect_disabled():
    collector = PerfEventsCollector()
    original = settings.PERF_EVENTS_ENABLED
    settings.PERF_EVENTS_ENABLED = False
    try:
        data = await collector.collect()
        assert data["available"] is False
        assert data["disabled"] is True
    finally:
        settings.PERF_EVENTS_ENABLED = original


@pytest.mark.asyncio
async def test_finalize_sample_marks_missing():
    collector = PerfEventsCollector()
    collector._current_time = "1.000000000"
    collector._current_events = {
        "cpu-clock": {"value": 1000.0, "unit": "msec"},
    }
    await collector._finalize_sample()
    latest = collector._latest
    assert latest is not None
    assert latest["available"] is False
    assert "missing_events" in latest
    assert "cycles" in latest["missing_events"]
