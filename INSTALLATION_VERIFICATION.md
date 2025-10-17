# Installation Verification Checklist

Use this checklist to verify your Academic Integrity Platform installation.

## ✅ Pre-Installation Checklist

- [ ] Docker installed and running (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] At least 16GB RAM available
- [ ] At least 50GB disk space available
- [ ] Ports 3000, 5432, 6379, 8000, 9000, 9200 are free

## ✅ File Verification

Run this command to verify all critical files exist:

```bash
bash verify_installation.sh
```

Or manually check:

### Core Application Files
- [ ] `backend/main.py` exists
- [ ] `ml_worker/ml_pipeline.py` exists
- [ ] `frontend/App.tsx` exists
- [ ] `mobile/App.tsx` exists
- [ ] `batch_processing/batch_processor.py` exists
- [ ] `collaboration/collaboration_system.py` exists
- [ ] `explainability/explainability_module.py` exists
- [ ] `integrations/integration_modules.py` exists
- [ ] `monitoring/monitoring_system.py` exists

### Configuration Files
- [ ] `.env.example` exists
- [ ] `docker-compose.yml` exists
- [ ] `backend/requirements.txt` exists
- [ ] `ml_worker/requirements-ml.txt` exists
- [ ] `frontend/package.json` exists
- [ ] `mobile/package.json` exists
- [ ] `nginx/nginx.conf` exists
- [ ] `monitoring/prometheus.yml` exists

### Dockerfiles
- [ ] `backend/Dockerfile` exists
- [ ] `ml_worker/Dockerfile` exists
- [ ] `frontend/Dockerfile` exists

### Scripts
- [ ] `backend/scripts/init_db.py` exists
- [ ] `backend/scripts/create_admin.py` exists
- [ ] `backend/scripts/entrypoint.sh` is executable
- [ ] `scripts/backup.sh` is executable
- [ ] `Makefile` exists

### Documentation
- [ ] `README.md` exists
- [ ] `QUICKSTART.md` exists
- [ ] `PROJECT_STATUS.md` exists

## ✅ Installation Steps

1. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your configuration
nano .env  # or vim, code, etc.
```
- [ ] Environment file configured
- [ ] Database password changed
- [ ] JWT secret generated
- [ ] SMTP settings configured (if needed)

2. **Build Services**
```bash
make build
# or
docker-compose build
```
- [ ] Backend image built successfully
- [ ] ML Worker image built successfully
- [ ] Frontend image built successfully
- [ ] No build errors

3. **Start Services**
```bash
make up
# or
docker-compose up -d
```
- [ ] PostgreSQL started
- [ ] Redis started
- [ ] Elasticsearch started
- [ ] MinIO started
- [ ] Backend API started
- [ ] ML Worker started
- [ ] Frontend started
- [ ] Nginx started
- [ ] Prometheus started
- [ ] Grafana started

4. **Verify Services**
```bash
docker-compose ps
```
All services should show as "healthy" or "running"

- [ ] postgres - healthy
- [ ] redis - healthy
- [ ] elasticsearch - healthy
- [ ] minio - healthy
- [ ] backend - running
- [ ] ml_worker - running
- [ ] frontend - running
- [ ] nginx - healthy

5. **Initialize Database**
```bash
make init
# or
docker-compose exec backend python scripts/init_db.py
```
- [ ] Database initialized successfully
- [ ] Tables created
- [ ] No errors

6. **Create Admin User**
```bash
make admin
# or
docker-compose exec backend python scripts/create_admin.py
```
- [ ] Admin user created
- [ ] Credentials saved securely

## ✅ Service Verification

### Backend API
```bash
curl http://localhost:8000/docs
```
- [ ] API documentation accessible
- [ ] No 500 errors

### Frontend
```bash
curl http://localhost:3000
```
- [ ] Frontend loads successfully
- [ ] No console errors (check browser)

### Database
```bash
docker-compose exec postgres psql -U aiplatform -d academic_integrity -c "\dt"
```
- [ ] Tables exist
- [ ] Database accessible

### Redis
```bash
docker-compose exec redis redis-cli ping
```
- [ ] Returns "PONG"

### Elasticsearch
```bash
curl http://localhost:9200
```
- [ ] Returns cluster info
- [ ] Status is "green" or "yellow"

### MinIO
- [ ] Access http://localhost:9001
- [ ] Login with credentials from .env
- [ ] Console loads

### Prometheus
- [ ] Access http://localhost:9090
- [ ] Targets page loads
- [ ] Targets are "UP"

### Grafana
- [ ] Access http://localhost:3001
- [ ] Login with credentials from .env
- [ ] Datasources configured

## ✅ Functional Testing

### 1. User Login
- [ ] Navigate to http://localhost:3000
- [ ] Login with admin credentials
- [ ] Dashboard loads successfully

### 2. Paper Upload
- [ ] Click "Upload Paper"
- [ ] Select a PDF file
- [ ] Fill in metadata
- [ ] Click "Analyze"
- [ ] Upload succeeds
- [ ] Processing starts

### 3. View Results
- [ ] Processing completes
- [ ] Risk score displayed
- [ ] Findings shown
- [ ] Report accessible

### 4. API Testing
```bash
# Get auth token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@example.com", "password": "your_password"}'

# Test authenticated endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/papers
```
- [ ] Authentication works
- [ ] API endpoints accessible
- [ ] Returns valid JSON

## ✅ Monitoring Verification

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
```
- [ ] No critical errors in logs
- [ ] Services logging properly

### Metrics
- [ ] Access http://localhost:9090/targets
- [ ] All targets showing "UP"
- [ ] Metrics being collected

### Alerts
- [ ] Grafana alerts configured
- [ ] Test alert triggers
- [ ] Email/Slack notifications work (if configured)

## ✅ Performance Verification

### Resource Usage
```bash
docker stats
```
- [ ] Memory usage reasonable (<80% of limit)
- [ ] CPU usage reasonable (<80% of limit)
- [ ] No services constantly restarting

### Response Times
- [ ] Frontend loads in <3 seconds
- [ ] API responses in <1 second
- [ ] File upload completes reasonably

## 🔴 Troubleshooting

If any checks fail:

1. **Check Logs**
```bash
docker-compose logs [service_name]
```

2. **Restart Service**
```bash
docker-compose restart [service_name]
```

3. **Rebuild Service**
```bash
docker-compose up -d --build [service_name]
```

4. **Check Resources**
```bash
docker system df
docker stats
```

5. **Clean and Restart**
```bash
make clean
make build
make up
make init
```

## ✅ Final Verification

- [ ] All services running
- [ ] No critical errors in logs
- [ ] Frontend accessible and functional
- [ ] API responding correctly
- [ ] Database queries working
- [ ] File upload successful
- [ ] Analysis completes
- [ ] Monitoring active
- [ ] Documentation reviewed

## 🎉 Success!

If all checks pass, your Academic Integrity Platform is ready to use!

Next steps:
1. Review [QUICKSTART.md](QUICKSTART.md) for usage guide
2. Configure institution-specific settings
3. Import existing papers (if any)
4. Set up regular backups
5. Configure production settings (if deploying to production)

---

For issues, see [README.md](README.md) troubleshooting section.
