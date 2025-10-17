.PHONY: help build up down logs clean test lint quickstart

help:
	@echo "Academic Integrity Platform - Makefile Commands"
	@echo "================================================"
	@echo "make quickstart   - 🚀 First-time setup and start"
	@echo "make build        - Build all Docker images"
	@echo "make up           - Start all services"
	@echo "make down         - Stop all services"
	@echo "make logs         - View logs"
	@echo "make clean        - Clean up containers and volumes"
	@echo "make test         - Run tests"
	@echo "make lint         - Run linters"
	@echo "make backup       - Backup database"
	@echo "make restore      - Restore database from backup"
	@echo "make init         - Initialize database"
	@echo "make admin        - Create admin user"
	@echo "make status       - Show service status"

quickstart:
	@echo "🚀 Starting Academic Integrity Platform..."
	@echo "Step 1: Building Docker images..."
	docker-compose build
	@echo "Step 2: Starting all services..."
	docker-compose up -d
	@echo "Step 3: Waiting for services to be ready..."
	@sleep 10
	@echo "Step 4: Initializing database..."
	-docker-compose exec -T backend python scripts/init_db.py
	@echo "Step 5: Creating admin user..."
	-docker-compose exec -T backend python scripts/create_admin.py
	@echo "================================================"
	@echo "✅ Setup complete!"
	@echo "================================================"
	@echo "Dashboard: http://localhost:8082"
	@echo "Backend API: http://localhost:8001"
	@echo "API Docs: http://localhost:8001/docs"
	@echo "================================================"
	@echo "Default credentials: admin / admin123"
	@echo "================================================"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✓ Services started"
	@echo "================================================"
	@echo "Dashboard: http://localhost:8082 (via Nginx)"
	@echo "Backend API: http://localhost:8001"
	@echo "Frontend Dev: http://localhost:4000"
	@echo "Grafana: http://localhost:4001"
	@echo "MinIO Console: http://localhost:9001"
	@echo "Elasticsearch: http://localhost:9200"
	@echo "Prometheus: http://localhost:9091"
	@echo "================================================"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

lint:
	docker-compose exec backend flake8 .
	docker-compose exec frontend npm run lint

backup:
	docker-compose exec backup /backup.sh

init:
	docker-compose exec backend python scripts/init_db.py

admin:
	docker-compose exec backend python scripts/create_admin.py

restart:
	docker-compose restart

ps:
	docker-compose ps

status:
	@echo "Service Status:"
	@docker-compose ps

shell-backend:
	docker-compose exec backend bash

shell-ml:
	docker-compose exec ml_worker bash

shell-frontend:
	docker-compose exec frontend sh

