.PHONY: help build up down logs clean test lint

help:
	@echo "Academic Integrity Platform - Makefile Commands"
	@echo "================================================"
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

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✓ Services started"
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "Grafana: http://localhost:3001"

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

shell-backend:
	docker-compose exec backend bash

shell-ml:
	docker-compose exec ml_worker bash

