# 🚀 SAGE.AI - Next Session Task List

**Created:** October 18, 2025
**Session Goal:** Complete remaining 11 critical security tasks
**Time Required:** ~14 hours total
**Current Progress:** 1/12 tasks complete (8%)

---

## ✅ COMPLETED THIS SESSION (1/12)

### 1. Rate Limiting Dependencies ✅
**Status:** Package added to requirements.txt
**What Was Done:**
- Added `slowapi==0.1.9` to `backend/requirements.txt`

**What's LEFT:**
- Add slowapi configuration to `backend/main.py`
- Apply rate limit decorators to endpoints
- Rebuild backend container
- Test rate limiting

**Code to Add to `backend/main.py`:**
```python
# After imports, around line 15
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# After app = FastAPI(...), around line 25
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Then decorate endpoints:
@app.post("/api/auth/signup")
@limiter.limit("5/minute")
async def signup(...):
    ...

@app.post("/api/auth/login")
@limiter.limit("10/minute")
async def login(...):
    ...

@app.post("/api/papers/upload")
@limiter.limit("20/hour")
async def upload(...):
    ...
```

**Test Commands:**
```bash
# Rebuild backend
docker-compose build backend
docker-compose up -d backend

# Test rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:8001/api/auth/signup \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"test$i@test.com\",\"password\":\"Test123\",\"full_name\":\"Test\"}"
done
# Should get 429 Too Many Requests after 5 requests
```

---

## 🔴 CRITICAL TASKS - DO THESE FIRST (7.5 hours)

### 2. HTTPS/SSL Certificates ⏳ STARTED
**Time:** 3 hours
**Priority:** CRITICAL
**Status:** SSL certificates need to be generated

**Quick Start:**
```bash
# 1. Create SSL directory and generate certificates
cd /Users/vladimirantoine/SAGE.AI/SAGE.AI
mkdir -p ssl
cd ssl

# 2. Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx-selfsigned.key \
  -out nginx-selfsigned.crt \
  -subj '/C=US/ST=California/L=San Francisco/O=SAGE.AI/OU=Development/CN=localhost'

# 3. Generate DH parameters (this takes 2-5 minutes)
openssl dhparam -out dhparam.pem 2048

# 4. Verify files created
ls -lh
# Should see: nginx-selfsigned.crt, nginx-selfsigned.key, dhparam.pem
```

**Create `nginx/sites-enabled/https.conf`:**
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name localhost;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name localhost;

    # SSL Certificates
    ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;

    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
    }
}
```

**Update `docker-compose.yml` (nginx section):**
```yaml
nginx:
  volumes:
    - ./ssl:/etc/nginx/ssl:ro  # Add this line
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro
```

**Test:**
```bash
docker-compose restart nginx
curl -k https://localhost/api/
```

---

### 3. Redis Password (1 hour)
**Priority:** HIGH

**Commands:**
```bash
# 1. Generate password
REDIS_PASSWORD=$(openssl rand -base64 32)
echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> .env

# 2. Update docker-compose.yml (redis section)
# Add to environment:
  REDIS_PASSWORD: ${REDIS_PASSWORD}
# Change command to:
  command: redis-server --requirepass ${REDIS_PASSWORD}

# 3. Update backend/main.py
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@redis:6379" if REDIS_PASSWORD else "redis://redis:6379"

# 4. Update backend/celery_app.py
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
broker_url = f"redis://:{REDIS_PASSWORD}@redis:6379/0" if REDIS_PASSWORD else "redis://redis:6379/0"

# 5. Restart services
docker-compose restart redis backend ml_worker

# 6. Test
docker exec academic_integrity_redis redis-cli -a $REDIS_PASSWORD PING
# Should return: PONG
```

---

### 4. Elasticsearch Security (2 hours)
**Priority:** HIGH

**Commands:**
```bash
# 1. Generate password
ELASTIC_PASSWORD=$(openssl rand -base64 32)
echo "ELASTIC_PASSWORD=$ELASTIC_PASSWORD" >> .env

# 2. Update docker-compose.yml (elasticsearch section)
environment:
  - xpack.security.enabled=true
  - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}

# 3. Update backend/main.py
from elasticsearch import Elasticsearch

ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
if ELASTIC_PASSWORD:
    es_client = Elasticsearch(
        ["http://elasticsearch:9200"],
        basic_auth=("elastic", ELASTIC_PASSWORD),
        verify_certs=False
    )

# 4. Restart
docker-compose restart elasticsearch backend

# 5. Test
curl -u elastic:$ELASTIC_PASSWORD http://localhost:9200/_cluster/health
```

---

### 5. CORS Configuration (30 minutes)
**Priority:** MEDIUM

**Update `backend/main.py`:**
```python
# Replace static origins list with environment variable
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:4000")
origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]
```

**Update `.env`:**
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:4000,http://localhost:8082,https://localhost
```

---

### 6. Generate Production JWT Secret (15 minutes)
**Priority:** CRITICAL

**Commands:**
```bash
# Generate new secret
JWT_SECRET_PRODUCTION=$(openssl rand -hex 32)
echo "JWT_SECRET_PRODUCTION=$JWT_SECRET_PRODUCTION" >> .env

# Document in PASSWORDS.txt
echo "Production JWT Secret: $JWT_SECRET_PRODUCTION" >> PASSWORDS.txt
```

---

### 7. Change Default Passwords (30 minutes)
**Priority:** CRITICAL

**Commands:**
```bash
# Generate strong passwords
cat >> .env << EOF

# Production Passwords (Generated $(date))
MINIO_PASSWORD_PRODUCTION=$(openssl rand -base64 32)
DB_PASSWORD_PRODUCTION=$(openssl rand -base64 32)
GRAFANA_PASSWORD_PRODUCTION=$(openssl rand -base64 32)
REDIS_PASSWORD_PRODUCTION=$(openssl rand -base64 32)
ELASTIC_PASSWORD_PRODUCTION=$(openssl rand -base64 32)
EOF

# Update PASSWORDS.txt with new values
```

**For deployment, use the _PRODUCTION passwords**

---

## 🟡 HIGH PRIORITY TASKS (6 hours)

### 8. Email Verification (4 hours)
**Priority:** HIGH

**Files to Create:**

**1. `backend/email_service.py`** (See IMPLEMENTATION_LOG.md for full code)

**2. Add to `backend/requirements.txt`:**
```
aiosmtplib==3.0.1
jinja2==3.1.2
```

**3. Update `backend/main.py`:**
- Add verification endpoints
- Update User model with verification_token and verification_token_expires
- Modify signup to send verification email

**4. Update `.env`:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourdomain.com
```

**Test:**
```bash
# Signup should send email
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123","full_name":"Test User"}'

# Check email for verification link
```

---

### 9. Load Testing (2 hours)
**Priority:** HIGH

**Commands:**
```bash
# Ensure all services running
docker-compose ps

# Run load test
cd backend
python3 load_test.py

# Monitor during test:
# Terminal 1: Backend logs
docker logs academic_integrity_backend -f

# Terminal 2: Database connections
watch -n 1 'docker exec academic_integrity_db psql -U aiplatform -d academic_integrity -c "SELECT count(*) FROM pg_stat_activity;"'

# Terminal 3: Redis stats
watch -n 1 'docker exec academic_integrity_redis redis-cli INFO stats | grep total_commands'

# Check results in Grafana
open http://localhost:4001
```

**Success Criteria:**
- All 1,800 requests complete
- Average response time < 500ms
- P95 < 1000ms
- No errors
- CPU < 80%
- Memory < 80%

---

## 🟢 MEDIUM PRIORITY TASKS (3 hours)

### 10. Backup/Restore Documentation (1 hour)

**Create `BACKUP_RESTORE_GUIDE.md`** (See IMPLEMENTATION_LOG.md for template)

**Test backup:**
```bash
# Manual backup
docker exec academic_integrity_db pg_dump -U aiplatform academic_integrity > backups/test_backup.sql

# Modify some data
docker exec -it academic_integrity_db psql -U aiplatform -d academic_integrity -c "INSERT INTO users (id, email, hashed_password, full_name) VALUES (gen_random_uuid(), 'test@test.com', 'hash', 'Test');"

# Restore
cat backups/test_backup.sql | docker exec -i academic_integrity_db psql -U aiplatform academic_integrity

# Verify data restored
```

---

### 11. Monitoring Alerts (2 hours)

**Create `monitoring/grafana/provisioning/alerting/alerts.yml`**
(See IMPLEMENTATION_LOG.md for full configuration)

**Configure in Grafana UI:**
1. Open http://localhost:4001
2. Go to Alerting → Contact Points
3. Add Email/Slack webhook
4. Test alert delivery

---

## 📊 Summary Checklist

**Before starting next session:**
- [ ] Review IMPLEMENTATION_LOG.md (has all code examples)
- [ ] Review PRODUCTION_ROADMAP.md (has full context)
- [ ] Check current service status: `docker-compose ps`
- [ ] Ensure you have `.env` file with current passwords

**Critical Path (Complete in Order):**
1. ✅ Rate limiting (finish implementation in main.py)
2. HTTPS/SSL certificates
3. Redis password
4. Elasticsearch security
5. CORS configuration
6. Production JWT secret
7. Change default passwords

**Then:**
8. Email verification
9. Load testing
10. Backup/restore docs
11. Monitoring alerts

**Final Steps:**
12. Complete testing
13. Update all documentation
14. Git commit and push
15. Deploy to staging/production

---

## 🔧 Quick Commands Reference

**Check Service Status:**
```bash
docker-compose ps
docker logs academic_integrity_backend --tail 50
```

**Restart Services:**
```bash
docker-compose restart backend
docker-compose restart nginx
```

**Rebuild After Changes:**
```bash
docker-compose build backend
docker-compose up -d backend
```

**Run Tests:**
```bash
pytest backend/tests/ -v
```

**Generate Passwords:**
```bash
openssl rand -base64 32  # For passwords
openssl rand -hex 32     # For JWT secret
```

---

## 📝 Files Modified This Session

1. `backend/requirements.txt` - Added slowapi
2. `IMPLEMENTATION_LOG.md` - Complete implementation guide (IMPORTANT!)
3. `PRODUCTION_ROADMAP.md` - Strategic roadmap
4. `NEXT_SESSION_TASKS.md` - This file

---

## 📝 Files to Create Next Session

1. `ssl/nginx-selfsigned.crt` - SSL certificate
2. `ssl/nginx-selfsigned.key` - SSL key
3. `ssl/dhparam.pem` - DH parameters
4. `nginx/sites-enabled/https.conf` - HTTPS config
5. `backend/email_service.py` - Email service
6. `BACKUP_RESTORE_GUIDE.md` - Backup docs
7. `monitoring/grafana/provisioning/alerting/alerts.yml` - Alerts

---

## 🎯 Session Goal

**Target:** Complete all 12 critical security tasks
**Time:** ~14 hours total, ~7 hours critical items
**Outcome:** Platform 100% production ready

**Current Status:** 85% → Target: 100%

---

## ⚠️ IMPORTANT NOTES

1. **IMPLEMENTATION_LOG.md has ALL the code examples** - refer to it constantly
2. **Test each item before moving to the next**
3. **Commit frequently** - after each major task
4. **Update PASSWORDS.txt** - keep credentials documented
5. **Document any issues** - add to IMPLEMENTATION_LOG.md

---

**Good luck! You have everything you need to complete the remaining tasks!** 🚀

**Most Important Files:**
- `IMPLEMENTATION_LOG.md` - Complete implementation details
- `PRODUCTION_ROADMAP.md` - Strategic overview
- `NEXT_SESSION_TASKS.md` - This file (step-by-step guide)
- `PASSWORDS.txt` - All credentials
