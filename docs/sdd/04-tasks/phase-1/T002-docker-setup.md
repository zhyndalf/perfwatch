# T002: Docker Setup

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 1 - Foundation |
| **Estimated Time** | 1-2 hours |
| **Dependencies** | T001 (Project Scaffold) |
| **Status** | ✅ COMPLETED |

---

## Objective

Create Docker Compose configuration to run all services: PostgreSQL, FastAPI backend, and Vue.js frontend.

---

## Context

Docker Compose provides:
- Consistent development environment
- Easy setup with single command
- Service orchestration
- Environment variable management

The backend container needs `--privileged` for perf stat access.

---

## Specifications

Reference documents:
- [Architecture](../../02-specification/architecture.md)
- [Principles - Docker First](../../01-constitution/principles.md#4-docker-first-development)

---

## Acceptance Criteria

### Docker Compose
- [x] `docker-compose.yml` created with all services
- [x] Backend service configured (FastAPI)
- [x] Frontend service configured (Vue/Nginx)
- [x] Database service configured (PostgreSQL)
- [x] Network configuration correct
- [x] Volume mounts for persistence

### Dockerfiles
- [x] `backend/Dockerfile` created
- [x] Python 3.11+ base image
- [x] Dependencies installed
- [x] Development server runs
- [x] `frontend/Dockerfile` created
- [x] Node.js for build
- [x] Nginx for serving

### Configuration
- [x] `.env.example` with all variables
- [x] Database credentials configurable
- [x] JWT secret configurable
- [x] Port mappings documented

### Verification
- [x] `docker-compose up` starts without errors
- [x] All containers healthy
- [x] Can access frontend on localhost:3000
- [x] Backend responds on localhost:8000

---

## Implementation Details

### docker-compose.yml Structure

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-perfwatch}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-perfwatch}
      POSTGRES_DB: ${POSTGRES_DB:-perfwatch}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U perfwatch"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    privileged: true  # Required for perf stat
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-perfwatch}:${POSTGRES_PASSWORD:-perfwatch}@db:5432/${POSTGRES_DB:-perfwatch}
      - JWT_SECRET=${JWT_SECRET:-change-this-in-production}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    linux-tools-generic \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application
COPY . .

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Frontend Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### .env.example

```bash
# Database
POSTGRES_USER=perfwatch
POSTGRES_PASSWORD=perfwatch
POSTGRES_DB=perfwatch

# Backend
JWT_SECRET=change-this-in-production
JWT_EXPIRE_HOURS=24

# Admin user
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

---

## Files to Create

| File | Description |
|------|-------------|
| `docker-compose.yml` | Service orchestration |
| `backend/Dockerfile` | Backend container |
| `frontend/Dockerfile` | Frontend container |
| `frontend/nginx.conf` | Nginx configuration |
| `.env.example` | Environment template |
| `README.md` | Basic project readme |

---

## Verification Steps

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Check logs
docker-compose logs -f

# Test database connection
docker-compose exec db psql -U perfwatch -c "SELECT 1"

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Stop all
docker-compose down
```

---

## Implementation Notes

- Docker Engine 29.1.5 and Docker Compose v5.0.1 installed on Ubuntu 24.04
- Removed obsolete `version: '3.8'` from docker-compose.yml (no longer needed)
- Changed frontend Dockerfile to use `npm install` instead of `npm ci` (no package-lock.json)
- Changed `FROM node:20-alpine as build` to `FROM node:20-alpine AS build` (case sensitivity)
- Added basic Vue.js landing page with backend status check
- All services verified working:
  - PostgreSQL: healthy, responds to queries
  - Backend: http://localhost:8000/health returns `{"status":"healthy"}`
  - Frontend: http://localhost:3000 serves the Vue.js app

---

## Files Created/Modified

| File | Action |
|------|--------|
| `docker-compose.yml` | Created |
| `backend/Dockerfile` | Created |
| `backend/pyproject.toml` | Created |
| `backend/app/main.py` | Created |
| `backend/app/__init__.py` | Created |
| `frontend/Dockerfile` | Created |
| `frontend/nginx.conf` | Created |
| `frontend/package.json` | Created |
| `frontend/vite.config.js` | Created |
| `frontend/index.html` | Created |
| `frontend/src/main.js` | Created |
| `frontend/src/App.vue` | Created |
| `frontend/public/vite.svg` | Created |
| `.env.example` | Created |
| `README.md` | Created |
