# 🚀 SAGE.AI Deployment Guide

Complete guide for deploying the Academic Integrity Platform locally and in production.

---

## 📋 Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Production Deployment](#production-deployment)
5. [Service Architecture](#service-architecture)
6. [Troubleshooting](#troubleshooting)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🎯 Quick Start

**Get up and running in 5 minutes:**

```bash
# Clone the repository
git clone https://github.com/yourusername/SAGE.AI.git
cd SAGE.AI

# Copy environment configuration
cp .env.example .env

# Start everything with one command
make quickstart

# Wait for ~2 minutes for all services to start
# Then open: http://localhost:8082
```

**Default Login:**
- Username: `admin`
- Password: `admin123`

---

## 📦 Prerequisites

### Required Software

- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)
- **Git**
- **Make** (optional, but recommended)

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Storage | 20 GB | 50+ GB SSD |
| Network | 10 Mbps | 100+ Mbps |

### Installing Prerequisites

**macOS:**
```bash
brew install docker docker-compose
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install docker.io docker-compose make
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # Add current user to docker group
```

**Windows:**
- Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- Install [Make for Windows](http://gnuwin32.sourceforge.net/packages/make.htm) (optional)

---

## 💻 Local Development Setup

### Step 1: Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/SAGE.AI.git
cd SAGE.AI

# Copy environment file
cp .env.example .env

# Edit .env with your preferred text editor
nano .env  # or vim, code, etc.
```

### Step 2: Configure Environment Variables

Edit `.env` and update these important settings:

```bash
# Security (CHANGE THESE!)
JWT_SECRET=your_random_64_character_secret_here
SECRET_KEY=your_random_64_character_key_here
DB_PASSWORD=your_secure_database_password

# MinIO (CHANGE IN PRODUCTION!)
MINIO_SECRET_KEY=your_minio_secret_key

# Grafana (CHANGE IN PRODUCTION!)
GRAFANA_PASSWORD=your_grafana_password

# Email Configuration (optional for development)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
```

### Step 3: Build and Start Services

**Option A: Using Makefile (Recommended)**

```bash
# One-command setup
make quickstart
```

**Option B: Manual Setup**

```bash
# Build all Docker images
docker-compose build

# Start all services
docker-compose up -d

# Wait for services to be ready (check status)
docker-compose ps

# Initialize database
docker-compose exec backend python scripts/init_db.py

# Create admin user
docker-compose exec backend python scripts/create_admin.py
```

### Step 4: Verify Installation

```bash
# Check service status
make status

# View logs
make logs

# Or view specific service logs
docker-compose logs -f backend
docker-compose logs -f ml_worker
```

### Step 5: Access the Platform

Open your browser and navigate to:

- **Main Dashboard:** http://localhost:8082
- **API Documentation:** http://localhost:8001/docs
- **Grafana Monitoring:** http://localhost:4001
- **MinIO Console:** http://localhost:9001

---

## 🌐 Production Deployment

### Pre-Production Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate secure JWT secrets (64+ characters)
- [ ] Configure SSL/TLS certificates
- [ ] Set up domain DNS records
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Configure email alerts
- [ ] Review and adjust resource limits
- [ ] Enable monitoring and logging
- [ ] Test disaster recovery plan

### Production Environment Variables

Create a production `.env` file:

```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Security
JWT_SECRET=<generate-with-openssl-rand-hex-64>
SECRET_KEY=<generate-with-openssl-rand-hex-64>
DB_PASSWORD=<strong-password-32+chars>

# Database (use managed service in production)
DB_HOST=your-postgres-host.rds.amazonaws.com
DB_PORT=5432
DB_NAME=academic_integrity_prod

# Redis (use managed service)
REDIS_URL=redis://your-redis-cluster:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com/ws

# Email Alerts
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<your-sendgrid-api-key>
ALERT_RECIPIENTS=admin@yourdomain.com,security@yourdomain.com

# Slack Alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Rate Limiting (adjust based on traffic)
RATE_LIMIT_PER_MINUTE=1000
UPLOAD_RATE_LIMIT_PER_MINUTE=50

# Processing
MAX_UPLOAD_SIZE_MB=500
PROCESSING_TIMEOUT_SECONDS=1800
```

### SSL/TLS Configuration

1. Obtain SSL certificates (Let's Encrypt recommended):

```bash
# Install certbot
sudo apt install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

2. Update `nginx/nginx.conf` with SSL configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Strong SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Rest of nginx config...
}
```

3. Mount certificates in `docker-compose.yml`:

```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Kubernetes Deployment (Advanced)

For production-scale deployments:

```bash
# Apply Kubernetes configurations
kubectl apply -f kubernetes/deployment.yaml

# Check deployment status
kubectl get pods -n academic-integrity

# View logs
kubectl logs -f deployment/backend -n academic-integrity
```

See `kubernetes/deployment.yaml` for full configuration.

---

## 🏗️ Service Architecture

### All Services

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| **nginx** | 8082 | Reverse proxy & load balancer | http://localhost:8082/health |
| **backend** | 8001 | FastAPI REST API | http://localhost:8001/docs |
| **frontend** | 4000 | React development server | http://localhost:4000 |
| **postgres** | 5433 | PostgreSQL database | `pg_isready` |
| **redis** | 6379 | Cache & job queue | `redis-cli ping` |
| **elasticsearch** | 9200 | Full-text search | http://localhost:9200 |
| **minio** | 9000 | Object storage (S3-compatible) | http://localhost:9000 |
| **ml_worker** | - | ML processing (Celery) | Celery status |
| **celery_beat** | - | Task scheduler | Celery beat |
| **prometheus** | 9091 | Metrics collection | http://localhost:9091 |
| **grafana** | 4001 | Monitoring dashboards | http://localhost:4001 |

### Data Flow

```
User → Nginx (8082) → Frontend (4000) → Backend API (8001)
                                          ↓
                                     PostgreSQL (DB)
                                          ↓
                                     Redis (Queue)
                                          ↓
                                     ML Worker (Processing)
                                          ↓
                                     Elasticsearch (Index)
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `Bind for 0.0.0.0:8082 failed: port is already allocated`

**Solution:**
```bash
# Find and kill process using the port
lsof -ti:8082 | xargs kill -9

# Or change port in docker-compose.yml
ports:
  - "8083:80"  # Use 8083 instead
```

#### 2. Database Connection Refused

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres

# Check logs
docker-compose logs postgres

# Verify database initialization
docker-compose exec postgres psql -U aiplatform -d academic_integrity -c "\dt"
```

#### 3. Out of Memory

**Error:** `docker: Error response from daemon: OOM command not allowed`

**Solution:**
```bash
# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → 8GB+

# Or reduce service resource usage
docker-compose down
docker system prune -a  # Clean up unused resources
docker-compose up -d
```

#### 4. ML Worker Crashes

**Error:** `ml_worker_1 exited with code 137`

**Solution:**
```bash
# Increase memory allocation
# Edit docker-compose.yml:
ml_worker:
  deploy:
    resources:
      limits:
        memory: 4G  # Increase from default

# Disable GPU if not available
# Edit .env:
USE_GPU=false
```

#### 5. Frontend Build Fails

**Error:** `npm ERR! code ELIFECYCLE`

**Solution:**
```bash
# Clear node_modules and rebuild
docker-compose down
docker-compose exec frontend rm -rf node_modules package-lock.json
docker-compose up -d frontend

# Or rebuild from scratch
docker-compose build --no-cache frontend
```

### Checking Service Health

```bash
# Overall status
make status

# Individual service logs
docker-compose logs -f backend
docker-compose logs -f ml_worker
docker-compose logs -f frontend

# Enter service shell for debugging
make shell-backend
make shell-ml
make shell-frontend

# Check resource usage
docker stats
```

### Reset Everything

If all else fails, complete reset:

```bash
# WARNING: This deletes all data!
make clean
rm -rf postgres_data redis_data elasticsearch_data minio_data

# Start fresh
make quickstart
```

---

## 📊 Monitoring & Maintenance

### Accessing Monitoring Tools

**Grafana Dashboards:**
1. Open http://localhost:4001
2. Login: `admin` / `admin` (change in production!)
3. Pre-configured dashboards:
   - System Overview
   - API Performance
   - ML Worker Metrics
   - Database Performance

**Prometheus Metrics:**
- Direct access: http://localhost:9091
- Query metrics directly
- Set up custom alerts

### Backup & Restore

**Automated Backups:**

Backups run daily at midnight (configured in `docker-compose.yml`).

```bash
# Manual backup
make backup

# Backups stored in ./backups/
ls -lh backups/
```

**Restore from Backup:**

```bash
# Stop services
docker-compose down

# Restore specific backup
docker-compose run --rm backup sh -c \
  "psql -h postgres -U aiplatform academic_integrity < /backups/backup_2024-01-15.sql"

# Restart services
docker-compose up -d
```

### Log Management

**View Logs:**

```bash
# All services
make logs

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow logs with timestamps
docker-compose logs -f --timestamps backend
```

**Log Rotation:**

Logs are automatically rotated. Configure in `docker-compose.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "10"
```

### Performance Tuning

**Database Optimization:**

```sql
-- Connect to database
docker-compose exec postgres psql -U aiplatform -d academic_integrity

-- Analyze and optimize
ANALYZE;
VACUUM FULL;

-- Check slow queries
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Scaling Workers:**

```bash
# Scale ML workers (in docker-compose.yml)
docker-compose up -d --scale ml_worker=4

# Verify
docker-compose ps ml_worker
```

### Health Checks

Create a monitoring script (`scripts/health_check.sh`):

```bash
#!/bin/bash

# Check all critical services
services=("backend:8001" "frontend:3000" "postgres:5432" "redis:6379")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if nc -z localhost $port; then
        echo "✅ $name is UP"
    else
        echo "❌ $name is DOWN"
        # Send alert
        curl -X POST $SLACK_WEBHOOK_URL -d "{\"text\":\"⚠️ $name is DOWN\"}"
    fi
done
```

Run periodically with cron:
```bash
# Add to crontab
*/5 * * * * /path/to/SAGE.AI/scripts/health_check.sh
```

---

## 🎓 Additional Resources

- [README.md](README.md) - Complete project documentation
- [QUICKSTART.md](QUICKSTART.md) - Fast-track getting started guide
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Implementation details and statistics
- [API Documentation](http://localhost:8001/docs) - Interactive API docs (Swagger)

---

## 📞 Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section above
2. Review logs: `make logs`
3. Check service status: `make status`
4. Create an issue on GitHub
5. Contact: support@yourdomain.com

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Last Updated:** October 17, 2024
**Version:** 1.0.0
