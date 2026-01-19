# PerfWatch

Real-time system performance monitoring web application.

## Features

- **Real-time Metrics**: CPU, Memory, Disk, Network monitoring with 5-second updates
- **Interactive Charts**: Beautiful visualizations powered by ECharts
- **Process Monitoring**: Track individual process resource usage
- **WebSocket Updates**: Live data streaming to the browser
- **Dockerized**: Easy setup with Docker Compose

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Vue.js 3 + ECharts |
| Backend | FastAPI + WebSocket |
| Database | PostgreSQL |
| Deployment | Docker Compose |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/zhyndalf/perfwatch.git
   cd perfwatch
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

### Verify Setup

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Test backend health
curl http://localhost:8000/health

# Stop all services
docker-compose down
```

## Development

### Project Structure

```
perfwatch/
├── backend/           # FastAPI backend
│   ├── app/           # Application code
│   ├── alembic/       # Database migrations
│   └── tests/         # Backend tests
├── frontend/          # Vue.js frontend
│   └── src/           # Source code
├── docs/              # Documentation
│   └── sdd/           # Specification Driven Development docs
├── scripts/           # Utility scripts
├── docker-compose.yml # Service orchestration
└── .env.example       # Environment template
```

### Running Locally (Development)

**Backend:**
```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Documentation

See [docs/sdd/README.md](./docs/sdd/README.md) for detailed project documentation including:
- Architecture decisions
- API specifications
- Development roadmap
- Task tracking

## License

MIT License - see [LICENSE](./LICENSE) for details.
