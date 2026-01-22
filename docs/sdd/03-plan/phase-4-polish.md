# Phase 4: History & Polish

> Historical data storage, comparison features, and final polish

---

## Overview

| Aspect | Details |
|--------|---------|
| Duration | ~12 hours (5 sessions) |
| Tasks | T018-T022 |
| Goal | Production-ready application |
| Prerequisites | Phase 3 complete |

---

## Task Summary

| Task | Name | Est. Time | Status |
|------|------|-----------|--------|
| T018 | History Storage | 2-3 hrs | ⬜ Not Started |
| T019 | Comparison View | 2-3 hrs | ⬜ Not Started |
| T020 | Data Retention | 2-3 hrs | ⬜ Not Started |
| T021 | Settings Page | 2-3 hrs | ⬜ Not Started |
| T022 | Polish & Testing | 3-4 hrs | ⬜ Not Started |

---

## T018: History Storage {#t018}

**Objective**: Store metrics to PostgreSQL and provide query API.

**Task File**: [T018-history-storage.md](../04-tasks/phase-4/T018-history-storage.md)

**Deliverables**:
- Async database writes in aggregator
- Batch insert for efficiency
- History query endpoint
- Configurable storage intervals
- Data aggregation for queries

**Acceptance Criteria**:
- [ ] Metrics persisted to database
- [ ] No impact on real-time performance
- [ ] Query endpoint returns data
- [ ] Aggregation works correctly

---

## T019: Comparison View {#t019}

**Objective**: Implement time period comparison feature with dual modes (relative and custom range).

**Task File**: [T019-comparison-view.md](../04-tasks/phase-4/T019-comparison-view.md)

**Deliverables**:
- Comparison API endpoint with dual modes
- Relative comparison: period (hour, day, week) + compare_to (yesterday, last_week)
- Custom range comparison: 4 explicit timestamps
- Frontend comparison UI with mode selection
- Overlay chart display with full time series
- Summary statistics (current_avg, comparison_avg, change_%)

**Acceptance Criteria**:
- [x] Can compare using relative mode (period + compare_to)
- [x] Can compare using custom ranges (4 timestamps)
- [x] Custom ranges validated for same duration
- [x] Overlay chart shows both time series
- [x] Summary stats show averages and percentage changes
- [x] Returns full data_points arrays for both periods

---

## T020: Data Retention {#t020}

**Objective**: Implement automatic data cleanup and downsampling.

**Task File**: [T020-data-retention.md](../04-tasks/phase-4/T020-data-retention.md)

**Deliverables**:
- Background cleanup task
- Configurable retention period
- Downsampling old data (5s → 1h)
- Retention statistics
- Manual cleanup trigger

**Acceptance Criteria**:
- [ ] Data older than retention deleted
- [ ] Downsampling preserves trends
- [ ] Background job runs reliably
- [ ] Storage growth controlled

---

## T021: Settings Page {#t021}

**Objective**: Create settings UI for configuration management.

**Task File**: [T021-settings-page.md](../04-tasks/phase-4/T021-settings-page.md)

**Deliverables**:
- Settings page component
- Retention policy controls
- Password change form
- System info display
- Logout functionality

**Acceptance Criteria**:
- [ ] Can change retention settings
- [ ] Can change password
- [ ] System status displayed
- [ ] Settings persist correctly

---

## T022: Polish & Testing {#t022}

**Objective**: Final polish, error handling, and testing.

**Task File**: [T022-polish-testing.md](../04-tasks/phase-4/T022-polish-testing.md)

**Deliverables**:
- Comprehensive error handling
- Loading states everywhere
- Empty state designs
- Backend unit tests
- Frontend component tests
- E2E test for critical paths
- Documentation updates

**Acceptance Criteria**:
- [ ] No unhandled errors
- [ ] All loading states implemented
- [ ] Tests pass
- [ ] Documentation complete
- [ ] Ready for daily use

---

## Dependency Graph

```
T018 (History Storage)
  │
  ├──► T019 (Comparison View)
  │
  └──► T020 (Data Retention)
         │
         └──► T021 (Settings Page)
                │
                └──► T022 (Polish & Testing)
```

---

## Data Retention Strategy

### Storage Tiers

| Age | Resolution | Storage |
|-----|------------|---------|
| 0-7 days | 5 seconds | Raw data |
| 7-30 days | 1 hour | Downsampled |
| 30+ days | Deleted | - |

### Downsampling Process

```python
# Every hour, aggregate old data
async def downsample_old_data():
    # Find data older than 7 days
    cutoff = datetime.now() - timedelta(days=7)

    # Group by hour and calculate averages
    hourly_data = await aggregate_to_hourly(cutoff)

    # Replace 5-second data with hourly
    await replace_with_hourly(hourly_data)
```

### Cleanup Schedule

```
Daily at 3 AM:
1. Delete data older than retention period
2. Downsample data older than downsample threshold
3. VACUUM ANALYZE tables
4. Update retention statistics
```

---

## End State

After Phase 4 is complete:

1. **History**: Full historical query support
2. **Comparison**: Same-period comparison working
3. **Retention**: Automatic data management
4. **Settings**: Full configuration UI
5. **Quality**: Polished, tested, documented

### Final Verification Checklist

```markdown
## Functionality
- [ ] Dashboard shows live metrics
- [ ] All metric types displayed
- [ ] WebSocket reconnects on disconnect
- [ ] Login/logout works
- [ ] History page queries data
- [ ] Comparison shows overlay
- [ ] Settings save correctly
- [ ] Password change works
- [ ] Data retention runs

## Performance
- [ ] Dashboard loads < 2s
- [ ] Charts update smoothly
- [ ] No memory leaks (24hr test)
- [ ] DB queries < 500ms

## Reliability
- [ ] Graceful degradation for perf stat
- [ ] Handles network issues
- [ ] Recovers from DB connection loss
- [ ] No unhandled exceptions

## Documentation
- [ ] README complete
- [ ] SDD up to date
- [ ] API documented
- [ ] Deployment guide written
```

---

## Success Criteria for Project Completion

The project is considered complete when:

1. ✅ Real-time dashboard showing all specified metrics updating every 5 seconds
2. ✅ Historical data viewable with dual-mode time period comparison (relative and custom ranges)
3. ✅ User authentication working
4. ✅ All services running via `docker-compose up`
5. ✅ Data persists across container restarts
6. ✅ Automatic data retention working
7. ✅ No critical bugs or unhandled errors
8. ✅ Documentation sufficient for handoff

---

## Post-Completion

### Maintenance Tasks
- Monitor disk usage
- Review logs periodically
- Update dependencies
- Backup database

### Future Enhancements (Not in Scope)
- Multiple user support
- Remote monitoring
- Alerting system
- Custom dashboards
- Plugin system
