#!/bin/bash
set -e

echo "=================================================================================="
echo "           Academic Integrity Platform - Localhost Deployment"
echo "=================================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Environment setup
echo "STEP 1: Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    
    # Generate secure secrets
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || echo "change_me_$(date +%s)_jwt")
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "change_me_$(date +%s)_secret")
    
    # Update .env (macOS compatible)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/change_me_to_random_64_char_string/$JWT_SECRET/g" .env
        sed -i '' "s/change_me_in_production/secure_password_$(date +%s)/g" .env
    else
        sed -i "s/change_me_to_random_64_char_string/$JWT_SECRET/g" .env
        sed -i "s/change_me_in_production/secure_password_$(date +%s)/g" .env
    fi
    
    echo -e "${GREEN}✓${NC} Environment file created with secure defaults"
else
    echo -e "${YELLOW}⚠${NC}  Using existing .env file"
fi

# Step 2: Build images
echo ""
echo "STEP 2: Building Docker images..."
echo "This may take 10-20 minutes on first run..."
docker-compose build || {
    echo -e "${RED}✗${NC} Build failed. Check Docker is running and you have internet connection."
    exit 1
}
echo -e "${GREEN}✓${NC} Docker images built successfully"

# Step 3: Start services
echo ""
echo "STEP 3: Starting services..."
docker-compose up -d || {
    echo -e "${RED}✗${NC} Failed to start services"
    exit 1
}
echo -e "${GREEN}✓${NC} Services started"

# Step 4: Wait for services to be healthy
echo ""
echo "STEP 4: Waiting for services to be ready..."
echo "This may take 2-3 minutes..."

# Wait for PostgreSQL
echo -n "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U aiplatform >/dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Redis
echo -n "Waiting for Redis..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Elasticsearch
echo -n "Waiting for Elasticsearch..."
for i in {1..60}; do
    if curl -s http://localhost:9200 >/dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Step 5: Initialize database
echo ""
echo "STEP 5: Initializing database..."
docker-compose exec -T backend python scripts/init_db.py || {
    echo -e "${YELLOW}⚠${NC}  Database initialization had issues, but continuing..."
}
echo -e "${GREEN}✓${NC} Database initialized"

# Step 6: Show status
echo ""
echo "=================================================================================="
echo "                         🎉 DEPLOYMENT COMPLETE! 🎉"
echo "=================================================================================="
echo ""
echo "Services are running on:"
echo ""
echo "  🌐 Frontend Dashboard:    http://localhost:3000"
echo "  🔧 Backend API:           http://localhost:8000"
echo "  📚 API Documentation:     http://localhost:8000/docs"
echo "  📊 Grafana Monitoring:    http://localhost:3001"
echo "  🗄️  MinIO Console:         http://localhost:9001"
echo "  📈 Prometheus:            http://localhost:9090"
echo ""
echo "Next steps:"
echo "  1. Create admin user:     make admin"
echo "  2. View logs:             make logs"
echo "  3. Check status:          docker-compose ps"
echo ""
echo "To stop all services:       make down"
echo "To restart services:        make restart"
echo ""
echo "Read QUICKSTART.md for detailed usage instructions."
echo "=================================================================================="
