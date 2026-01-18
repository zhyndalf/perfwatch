# T002: Docker Setup

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 1 - Foundation |
| **Estimated Time** | 1-2 hours |
| **Dependencies** | T001 (Project Scaffold) |
| **Status** | ⬜ NOT_STARTED |

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

The backend container needs `--privileged` for perf_events access.

---

## Specifications

Reference documents:
- [Architecture](../../02-specification/architecture.md)
- [Principles - Docker First](../../01-constitution/principles.md#4-docker-first-development)

---

## Acceptance Criteria

### Docker Compose
- [ ] `docker-compose.yml` created with all services
- [ ] Backend service configured (FastAPI)
- [ ] Frontend service configured (Vue/Nginx)
- [ ] Database service configured (PostgreSQL)
- [ ] Network configuration correct
- [ ] Volume mounts for persistence

### Dockerfiles
- [ ] `backend/Dockerfile` created
- [ ] Python 3.11+ base image
- [ ] Dependencies installed
- [ ] Development server runs
- [ ] `frontend/Dockerfile` created
- [ ] Node.js for build
- [ ] Nginx for serving

### Configuration
- [ ] `.env.example` with all variables
- [ ] Database credentials configurable
- [ ] JWT secret configurable
- [ ] Port mappings documented

### Verification
- [ ] `docker-compose up` starts without errors
- [ ] All containers healthy
- [ ] Can access frontend on localhost:3000
- [ ] Backend responds on localhost:8000

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
    privileged: true  # Required for perf_events
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

*To be filled during implementation*

---

## Files Created/Modified

*To be filled during implementation*
