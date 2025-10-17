# Academic Integrity Platform - Quick Start Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)
- [Git](https://git-scm.com/downloads)
- [Make](https://www.gnu.org/software/make/) (optional, for convenience)

### System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB+ free space
- **GPU**: NVIDIA GPU with CUDA 11.8+ (optional, for ML acceleration)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd SAGE.AI

# Copy environment template
cp .env.example .env

# Edit .env with your configuration (use a text editor)
nano .env
```

### Important Environment Variables to Change:

```env
# Database (CHANGE THESE!)
DB_PASSWORD=your_secure_password_here

# Security (GENERATE RANDOM STRINGS!)
JWT_SECRET=your_random_64_char_jwt_secret
SECRET_KEY=your_random_64_char_secret

# MinIO (CHANGE THESE!)
MINIO_SECRET_KEY=your_secure_minio_password

# Email (for alerts)
SMTP_USER=your_email@domain.com
SMTP_PASSWORD=your_email_password

# Grafana (CHANGE THIS!)
GRAFANA_PASSWORD=your_grafana_password
```

## Step 2: Build and Start

```bash
# Option A: Using Make (recommended)
make build
make up

# Option B: Using Docker Compose directly
docker-compose build
docker-compose up -d
```

This will start all services:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Elasticsearch (port 9200)
- MinIO (port 9000, 9001)
- Backend API (port 8000)
- Frontend (port 3000)
- Prometheus (port 9090)
- Grafana (port 3001)

## Step 3: Initialize Database

```bash
# Option A: Using Make
make init

# Option B: Using Docker Compose
docker-compose exec backend python scripts/init_db.py
```

## Step 4: Create Admin User

```bash
# Option A: Using Make
make admin

# Option B: Using Docker Compose
docker-compose exec backend python scripts/create_admin.py
```

Follow the prompts to create your admin account.

## Step 5: Access the Platform

Open your browser and navigate to:

- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Grafana Monitoring**: http://localhost:3001
  - Username: `admin`
  - Password: (as set in .env)
- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: (as set in .env)
- **Prometheus**: http://localhost:9090

## Step 6: Upload Your First Paper

1. Go to http://localhost:3000
2. Login with your admin credentials
3. Click on "Upload Paper"
4. Select a PDF file
5. Fill in metadata
6. Click "Analyze"

The system will:
- Extract text from the PDF
- Run plagiarism detection
- Perform statistical anomaly detection
- Check for image manipulation
- Generate a comprehensive report

## Common Commands

```bash
# View logs
make logs
# or
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f ml_worker

# Check service status
make ps
# or
docker-compose ps

# Restart services
make restart
# or
docker-compose restart

# Stop all services
make down
# or
docker-compose down

# Stop and remove all data
make clean
# or
docker-compose down -v

# Run tests
make test

# Backup database
make backup

# Access backend shell
make shell-backend
# or
docker-compose exec backend bash
```

## Troubleshooting

### Services won't start

```bash
# Check if ports are already in use
netstat -tuln | grep -E '3000|5432|6379|8000|9000|9200'

# Check Docker logs
docker-compose logs

# Restart Docker daemon
sudo systemctl restart docker  # Linux
# or restart Docker Desktop on Mac/Windows
```

### Database connection errors

```bash
# Wait for PostgreSQL to be ready
docker-compose logs postgres

# Check if PostgreSQL is healthy
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### Out of memory errors

```bash
# Increase Docker memory limit (Docker Desktop)
# Go to Docker Desktop → Settings → Resources → Memory
# Set to at least 8GB (16GB recommended)

# Or reduce worker replicas in docker-compose.yml
# Change ml_worker replicas from 2 to 1
```

### ML models not downloading

```bash
# ML models are downloaded on first start
# This can take 10-20 minutes depending on internet speed
# Check progress:
docker-compose logs ml_worker

# If download fails, restart ml_worker:
docker-compose restart ml_worker
```

### Frontend build errors

```bash
# Clear and rebuild
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

## Development Mode

For development with hot-reload:

```bash
# Backend (with auto-reload)
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (with hot-reload)
cd frontend
npm install
npm run dev

# In separate terminal, start dependencies only:
docker-compose up -d postgres redis elasticsearch minio
```

## Production Deployment

For production deployment, see [README.md](README.md) section on Kubernetes deployment.

Key production changes:
1. Use strong passwords and secrets
2. Enable SSL/TLS
3. Configure proper backups
4. Set up monitoring alerts
5. Use external managed databases
6. Configure CDN for frontend
7. Set DEBUG=false

## Need Help?

- Documentation: [README.md](README.md)
- Issues: Create an issue in the repository
- Email: support@academic-integrity.com

## Next Steps

1. Configure your institution settings
2. Import existing papers (bulk upload via API)
3. Set up email notifications
4. Configure Grafana dashboards
5. Train custom ML models with your data
6. Integrate with your journal/LMS systems

Enjoy using the Academic Integrity Platform! 🎓
