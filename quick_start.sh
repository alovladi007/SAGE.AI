#!/bin/bash

echo "=========================================="
echo " Academic Integrity Platform - Quick Start"
echo "=========================================="
echo ""
echo "Starting essential services only (PostgreSQL, Redis, Elasticsearch, MinIO)..."
echo ""

# Setup environment if needed
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file"
fi

# Start only infrastructure services
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "✓ Infrastructure services starting..."
echo ""
echo "Services:"
echo "  - PostgreSQL:     localhost:5432"
echo "  - Redis:          localhost:6379"
echo "  - Elasticsearch:  localhost:9200"
echo "  - MinIO:          localhost:9000"
echo ""
echo "Check status: docker-compose -f docker-compose.dev.yml ps"
echo "View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "Stop: docker-compose -f docker-compose.dev.yml down"
echo ""
echo "Next: You can now run the backend and frontend locally for development."
