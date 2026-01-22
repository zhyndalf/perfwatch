# PerfWatch Learnings

> Lessons learned during implementation

---

## How to Use This File

Document things learned during implementation that might be useful later:
- Gotchas and workarounds
- Performance insights
- Useful techniques discovered
- Mistakes to avoid

---

## General

### SDD Approach
- **Learned**: File-based specs work well for AI-assisted development
- **Why**: Context can be loaded fresh each conversation
- **Tip**: Keep CURRENT_TASK.md always up to date

---

## Backend

*To be filled as we implement*

### Python/FastAPI
- (Learnings about async patterns, etc.)

### SQLAlchemy
- (Learnings about async ORM usage)

### perf stat
- (Learnings about hardware counters)

---

## Frontend

*To be filled as we implement*

### Vue.js 3
- (Learnings about Composition API patterns)

### ECharts
- (Learnings about real-time chart updates)

### WebSocket
- (Learnings about connection management)

---

## Docker

*To be filled as we implement*

### Docker Compose
- (Learnings about service orchestration)

### Privileged Mode
- (Learnings about perf stat access)

---

## Database

*To be filled as we implement*

### PostgreSQL
- (Learnings about JSONB performance)

### Migrations
- (Learnings about async Alembic)

---

## Performance

*To be filled as we implement*

### Collection Overhead
- (Learnings about metric collection cost)

### WebSocket Throughput
- (Learnings about streaming performance)

### Browser Performance
- (Learnings about chart rendering)

---

## Mistakes Made

*Document mistakes to avoid repeating*

### Example Format
```
### [Date] - Brief Description
**What happened**: Description of the mistake
**Root cause**: Why it happened
**Solution**: How it was fixed
**Prevention**: How to avoid in future
```

---

## Useful References

*Links and resources that were helpful*

- [FastAPI Async SQLAlchemy](https://fastapi.tiangolo.com/advanced/async-sql-databases/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [ECharts Documentation](https://echarts.apache.org/en/option.html)
- [psutil Documentation](https://psutil.readthedocs.io/en/latest/)
- [perf-stat man page](https://man7.org/linux/man-pages/man1/perf-stat.1.html)
