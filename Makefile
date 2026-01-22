.PHONY: help docker-up docker-down docker-build docker-logs backend-test backend-lint backend-shell frontend-build frontend-dev frontend-shell db-migrate db-upgrade db-downgrade db-shell clean docker-buildx-setup docker-build-multiarch docker-build-arm docker-push-multiarch docker-buildx-info

##@ General

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\n\033[1mUsage:\033[0m\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker

docker-up: ## Start all services (backend, frontend, database)
	docker compose up -d

docker-down: ## Stop all services
	docker compose down

docker-down-volumes: ## Stop all services and remove volumes (WARNING: deletes database)
	docker compose down -v

docker-build: ## Rebuild all Docker images
	docker compose build

docker-build-backend: ## Rebuild backend Docker image
	docker compose build backend

docker-build-frontend: ## Rebuild frontend Docker image
	docker compose build frontend

docker-logs: ## View logs from all services
	docker compose logs -f

docker-logs-backend: ## View backend logs only
	docker compose logs -f backend

docker-logs-frontend: ## View frontend logs only
	docker compose logs -f frontend

docker-restart: ## Restart all services
	docker compose restart

##@ Backend

backend-test: ## Run backend tests (pytest)
	docker compose run --rm backend pytest tests/ -v

backend-test-fast: ## Run backend tests in parallel (faster)
	docker compose run --rm backend pytest tests/ -v -n auto

backend-test-coverage: ## Run tests with coverage report
	docker compose run --rm backend pytest tests/ --cov=app --cov-report=html

backend-lint: ## Run black and isort on backend code
	docker compose run --rm backend black app/ tests/
	docker compose run --rm backend isort app/ tests/

backend-shell: ## Open a shell in the backend container
	docker compose exec backend bash

backend-python: ## Open a Python REPL in the backend container
	docker compose exec backend python

##@ Frontend

frontend-build: ## Build frontend for production
	docker compose exec frontend npm run build

frontend-dev: ## Start frontend development server
	docker compose exec frontend npm run dev

frontend-preview: ## Preview production build
	docker compose exec frontend npm run preview

frontend-lint: ## Run ESLint on frontend code
	docker compose exec frontend npm run lint

frontend-shell: ## Open a shell in the frontend container
	docker compose exec frontend sh

frontend-install: ## Install frontend dependencies
	docker compose exec frontend npm install

##@ Database

db-migrate: ## Create a new database migration
	@read -p "Enter migration message: " msg; \
	docker compose exec backend alembic revision --autogenerate -m "$$msg"

db-upgrade: ## Apply all pending migrations
	docker compose exec backend alembic upgrade head

db-downgrade: ## Rollback one migration
	docker compose exec backend alembic downgrade -1

db-shell: ## Open PostgreSQL shell
	docker compose exec db psql -U perfwatch -d perfwatch

db-status: ## Check database connection status
	curl http://localhost:8000/api/db-status

##@ Development

dev: docker-up ## Start development environment (alias for docker-up)

stop: docker-down ## Stop development environment (alias for docker-down)

restart: docker-restart ## Restart all services

logs: docker-logs ## View logs (alias for docker-logs)

test: backend-test ## Run tests (alias for backend-test)

##@ Cleanup

clean: ## Remove build artifacts and cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true

clean-docker: docker-down-volumes ## Clean Docker volumes and images
	docker compose rm -f
	docker image prune -f

##@ Health Checks

health: ## Check health of all services
	@echo "Backend Health:"
	@curl -s http://localhost:8000/health | jq . || echo "Backend not responding"
	@echo "\nDatabase Status:"
	@curl -s http://localhost:8000/api/db-status | jq . || echo "Database check failed"
	@echo "\nFrontend:"
	@curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:3000 || echo "Frontend not responding"

##@ Quick Start

setup: docker-build docker-up db-upgrade ## Complete setup (build, start, migrate)
	@echo "\n✅ Setup complete!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Login: admin / admin123"

##@ Multi-Architecture Builds

BUILDX_BUILDER := perfwatch-builder
REGISTRY := ghcr.io/zhyndalf
BACKEND_IMAGE := $(REGISTRY)/perfwatch-backend
FRONTEND_IMAGE := $(REGISTRY)/perfwatch-frontend

docker-buildx-setup: ## Set up Docker Buildx for multi-arch builds
	@docker buildx inspect $(BUILDX_BUILDER) >/dev/null 2>&1 || \
		docker buildx create --name $(BUILDX_BUILDER) --driver docker-container --bootstrap
	@docker buildx use $(BUILDX_BUILDER)
	@echo "✅ Buildx builder '$(BUILDX_BUILDER)' is ready"

docker-build-multiarch: docker-buildx-setup ## Build multi-arch images (amd64 + arm64) locally
	@echo "Building backend for linux/amd64,linux/arm64..."
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(BACKEND_IMAGE):latest ./backend
	@echo "Building frontend for linux/amd64,linux/arm64..."
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(FRONTEND_IMAGE):latest ./frontend
	@echo "✅ Multi-arch build complete (not pushed)"

docker-build-arm: docker-buildx-setup ## Build ARM64 images and load locally (for testing)
	@echo "Building backend for linux/arm64..."
	docker buildx build --platform linux/arm64 \
		-t perfwatch-backend:arm64-test --load ./backend
	@echo "Building frontend for linux/arm64..."
	docker buildx build --platform linux/arm64 \
		-t perfwatch-frontend:arm64-test --load ./frontend
	@echo "✅ ARM64 images loaded locally"
	@echo "Test with: docker run --rm perfwatch-backend:arm64-test uname -m"

docker-push-multiarch: docker-buildx-setup ## Build and push multi-arch images to GHCR
	@echo "Building and pushing backend..."
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(BACKEND_IMAGE):latest --push ./backend
	@echo "Building and pushing frontend..."
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(FRONTEND_IMAGE):latest --push ./frontend
	@echo "✅ Multi-arch images pushed to $(REGISTRY)"

docker-buildx-info: ## Show buildx builder info and platforms
	@docker buildx ls
	@echo ""
	@docker buildx inspect $(BUILDX_BUILDER) 2>/dev/null || echo "Builder '$(BUILDX_BUILDER)' not created. Run 'make docker-buildx-setup'"

