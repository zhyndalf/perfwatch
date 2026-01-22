# PerfWatch Development Guide

This guide provides detailed information for developing and debugging PerfWatch.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [IDE Configuration](#ide-configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Debugging](#debugging)
- [Common Issues](#common-issues)
- [Database Migrations](#database-migrations)
- [Performance Tips](#performance-tips)

---

## Prerequisites

### Required

- **Docker Desktop** (v24.0+) & Docker Compose
- **Git**
- **Linux Host** (for perf stat + PMU support; VMs need PMU passthrough)
- **perf** (linux-perf or linux-tools) for perf_events counters

### Optional (for local development without Docker)

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**

---

## Development Setup

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/zhyndalf/perfwatch.git
cd perfwatch

# Start all services
make docker-up
# Or: docker compose up -d

# Run migrations
make db-upgrade
# Or: docker compose exec backend alembic upgrade head

# Verify services
make health
# Or: curl http://localhost:8000/health
```

### Option 2: Local Development (Without Docker)

**Backend:**
```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://perfwatch:perfwatch@localhost:5432/perfwatch"
export JWT_SECRET="your-secret-key"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="admin123"
export PERF_EVENTS_ENABLED="true"
export PERF_EVENTS_CPU_CORES="all"
export PERF_EVENTS_INTERVAL_MS="1000"

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Or build for production
npm run build
npm run preview
```

**Database (PostgreSQL):**
```bash
# Install PostgreSQL 15
sudo apt install postgresql-15

# Create database and user
sudo -u postgres psql
CREATE DATABASE perfwatch;
CREATE USER perfwatch WITH PASSWORD 'perfwatch';
GRANT ALL PRIVILEGES ON DATABASE perfwatch TO perfwatch;
\q
```

---

## IDE Configuration

### VS Code

**Recommended Extensions:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Vue Language Features (Vue.volar)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Docker (ms-azuretools.vscode-docker)

**Settings (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm

1. **Open Project**: File → Open → Select `perfwatch` directory
2. **Configure Interpreter**:
   - Settings → Project → Python Interpreter
   - Add → Docker Compose → Select `backend` service
3. **Enable Pytest**: Settings → Tools → Python Integrated Tools → Default test runner: pytest
4. **Configure Black**: Settings → Tools → Black → Enable on save

---

## Running the Application

### Using Makefile (Easiest)

```bash
# Start everything
make setup

# Run tests
make test

# View logs
make logs

# Stop services
make stop

# Clean up
make clean
```

### Using Docker Compose Directly

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart a service
docker compose restart backend

# Stop services
docker compose down
```

### Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | admin / admin123 |
| Backend API | http://localhost:8000 | - |
| API Docs (Swagger) | http://localhost:8000/docs | - |
| PostgreSQL | localhost:5432 | perfwatch / perfwatch |

---

## Testing

### Backend Tests

```bash
# Run all tests
make backend-test
# Or: docker compose run --rm backend pytest tests/ -v

# Run specific test file
docker compose run --rm backend pytest tests/test_auth.py -v

# Run specific test function
docker compose run --rm backend pytest tests/test_auth.py::TestLoginEndpoint::test_login_success -v

# Run tests matching pattern
docker compose run --rm backend pytest tests/ -k "collector" -v

# Run tests in parallel (faster)
make backend-test-fast
# Or: docker compose run --rm backend pytest tests/ -n auto

# Generate coverage report
make backend-test-coverage
# Then open: backend/htmlcov/index.html
```

### Frontend Tests

```bash
# Run unit tests (when implemented)
docker compose exec frontend npm test

# Run E2E tests (when implemented)
docker compose exec frontend npm run test:e2e
```

---

## Debugging

### Backend Debugging

**Using print statements:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Debug info: {variable}")
logger.error(f"Error occurred: {error}")
```

**Using VS Code debugger:**
1. Add breakpoint in code
2. Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```
3. Press F5 to start debugging

**Using pdb:**
```python
# Add this line where you want to break
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()
```

### WebSocket Debugging

**Using wscat (command line):**
```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
# 1. First, get a JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Connect with token
wscat -c "ws://localhost:8000/api/ws/metrics?token=$TOKEN"

# You should see metrics streaming in JSON format
```

**Using Browser DevTools:**
1. Open http://localhost:3000
2. Open DevTools (F12) → Network tab
3. Filter: WS (WebSocket)
4. Click on the WebSocket connection
5. View Messages tab to see data flow

### Database Debugging

**Check connection:**
```bash
make db-status
# Or: curl http://localhost:8000/api/db-status
```

**Query database directly:**
```bash
make db-shell
# Or: docker compose exec db psql -U perfwatch -d perfwatch

# Useful queries:
SELECT COUNT(*) FROM metrics_snapshot;
SELECT metric_type, COUNT(*) FROM metrics_snapshot GROUP BY metric_type;
SELECT * FROM users;
SELECT * FROM archive_policy;
```

**View recent snapshots:**
```sql
SELECT
    timestamp,
    metric_type,
    metric_data->>'usage_percent' as cpu_usage
FROM metrics_snapshot
WHERE metric_type = 'cpu'
ORDER BY timestamp DESC
LIMIT 10;
```

### Frontend Debugging

**Vue DevTools:**
1. Install Vue DevTools browser extension
2. Open DevTools → Vue tab
3. Inspect components, state, and events

**Network Debugging:**
1. Open DevTools (F12) → Network tab
2. Filter: XHR/Fetch for API calls
3. Check request/response payloads
4. Verify JWT tokens in Authorization headers

---

## Common Issues

### Backend Won't Start

**Issue**: `ImportError` or module not found

**Solution**:
```bash
# Rebuild backend image
docker compose build backend

# Or install dependencies locally
cd backend
pip install -e ".[dev]"
```

**Issue**: Database connection failed

**Solution**:
```bash
# Check if database is running
docker compose ps

# Check database logs
docker compose logs db

# Restart database
docker compose restart db

# Run migrations
make db-upgrade
```

### Frontend Won't Build

**Issue**: `npm` errors or missing dependencies

**Solution**:
```bash
# Rebuild frontend image
docker compose build frontend

# Or reinstall dependencies
docker compose exec frontend npm install

# Clear cache
docker compose exec frontend npm cache clean --force
```

### WebSocket Connection Failed

**Issue**: WebSocket fails to connect or disconnects immediately

**Checklist**:
1. **Check token**: Ensure JWT token is valid
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```
2. **Check backend logs**:
   ```bash
   docker compose logs backend | grep -i websocket
   ```
3. **Verify CORS settings**: Check `app/main.py` CORS configuration

### Tests Failing

**Issue**: Tests pass locally but fail in Docker

**Solution**:
```bash
# Ensure test database is clean
docker compose down -v
docker compose up -d

# Run tests with verbose output
docker compose run --rm backend pytest tests/ -vv --tb=long
```

**Issue**: Specific test fails intermittently

**Possible causes**:
- Race condition in async tests
- Time-dependent logic
- Database state not cleaned between tests

**Debug**:
```bash
# Run the test multiple times
for i in {1..10}; do
  docker compose run --rm backend pytest tests/test_file.py::test_name -v
done
```

### Performance Issues

**Backend slow response:**
```bash
# Check collector performance
docker compose logs backend | grep "collection took"

# Check database query times
# Add to your code:
import time
start = time.time()
# ... database query ...
logger.info(f"Query took {time.time() - start:.3f}s")
```

**Frontend slow rendering:**
- Check browser console for errors
- Use Vue DevTools Performance tab
- Verify WebSocket message frequency (should be every 5s)

---

## Database Migrations

### Creating Migrations

```bash
# After modifying models in backend/app/models/
make db-migrate
# Follow prompt to enter migration message

# Or manually:
docker compose exec backend alembic revision --autogenerate -m "add new column"
```

### Reviewing Migrations

```bash
# Check generated migration file
cat backend/alembic/versions/XXXX_your_migration.py

# Verify changes before applying
```

### Applying Migrations

```bash
# Apply all pending migrations
make db-upgrade

# Or apply one by one
docker compose exec backend alembic upgrade +1
```

### Rolling Back Migrations

```bash
# Rollback last migration
make db-downgrade

# Rollback to specific revision
docker compose exec backend alembic downgrade <revision_id>

# Rollback all
docker compose exec backend alembic downgrade base
```

---

## Performance Tips

### Backend

1. **Enable connection pooling** (already configured in `database.py`)
2. **Use async sessions** for all database operations
3. **Batch database operations** when possible
4. **Monitor collector execution time**:
   ```python
   logger.debug(f"{self.name} collection took {duration:.3f}s")
   ```

### Frontend

1. **Debounce rapid updates** (already implemented for charts)
2. **Use `v-memo` for expensive renders**
3. **Lazy load heavy components**:
   ```js
   const HeavyChart = defineAsyncComponent(() =>
     import('./components/HeavyChart.vue')
   )
   ```

### Database

1. **Add indexes for frequent queries**:
   ```python
   timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
   ```
2. **Use JSONB operators** for efficient querying:
   ```sql
   SELECT * FROM metrics_snapshot
   WHERE metric_data->>'cpu_usage' > '80';
   ```
3. **Regular VACUUM** (automatic in Docker setup)

---

## Useful Commands Cheat Sheet

```bash
# Quick Start
make setup                    # Setup entire environment
make dev                      # Start development

# Development
make logs                     # View all logs
make backend-shell            # Backend shell
make frontend-shell           # Frontend shell
make db-shell                 # Database shell

# Testing
make test                     # Run backend tests
make backend-test-coverage    # Tests with coverage

# Database
make db-migrate               # Create migration
make db-upgrade               # Apply migrations
make db-status                # Check DB status

# Cleanup
make clean                    # Remove artifacts
make docker-down-volumes      # Remove all data (WARNING)

# Health Check
make health                   # Check all services
```

---

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Project SDD**: `docs/sdd/`
- **Architecture**: `docs/sdd/02-specification/architecture.md`
- **Contributing**: `CONTRIBUTING.md`

---

## Getting Help

If you encounter issues not covered here:

1. Check `CLAUDE.md` for AI-friendly documentation
2. Search GitHub Issues: https://github.com/zhyndalf/perfwatch/issues
3. Review backend logs: `make logs`
4. Check database status: `make db-status`

Happy coding! 🚀
