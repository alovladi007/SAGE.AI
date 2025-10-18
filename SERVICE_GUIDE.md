# SAGE.AI Platform - Service Access Guide

Complete guide to accessing and using all services in the SAGE.AI Academic Integrity Platform.

---

## 🌐 Service URLs Overview

| Service | URL | Purpose | Authentication |
|---------|-----|---------|----------------|
| **Backend API** | http://localhost:8001 | Main REST API | JWT Token |
| **API Documentation** | http://localhost:8001/docs | Interactive API docs | None |
| **Frontend** | http://localhost:8082 | Web UI | JWT Token |
| **MinIO Console** | http://localhost:9001 | File storage admin | minioadmin/minioadmin |
| **Grafana** | http://localhost:4001 | Monitoring dashboards | admin/admin |
| **Prometheus** | http://localhost:9091 | Metrics database | None |
| **Elasticsearch** | http://localhost:9200 | Search engine | None |
| **Redis** | localhost:6379 | Cache/Queue | None |

---

## 1️⃣ Backend API - http://localhost:8001

### What It Does
The **FastAPI backend** handles all business logic:
- User authentication (signup, login, JWT tokens)
- PDF paper uploads and processing
- ML-powered plagiarism detection
- Similarity checking across papers
- Citation analysis
- Statistical anomaly detection

### How to Use It

#### A. Check if it's running:
```bash
curl http://localhost:8001/
```

**Response:**
```json
{
  "name": "SAGE.AI Academic Integrity Platform",
  "version": "1.0.0",
  "status": "operational",
  "environment": "development"
}
```

#### B. Create a new user account:
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "password": "SecurePass123",
    "full_name": "Your Name",
    "institution": "Your University"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "your.email@example.com",
    "full_name": "Your Name",
    "role": "user"
  }
}
```

**Save this token!** You'll need it for authenticated requests.

#### C. Login (if you already have an account):
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "password": "SecurePass123"
  }'
```

#### D. Upload a research paper (PDF):
```bash
# Replace YOUR_TOKEN with the token from signup/login
curl -X POST http://localhost:8001/api/papers/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/your/paper.pdf"
```

**Response:**
```json
{
  "paper_id": "uuid-of-paper",
  "job_id": "celery-job-id",
  "status": "queued",
  "message": "Paper uploaded successfully and queued for processing"
}
```

#### E. Search for papers:
```bash
curl "http://localhost:8001/api/papers/search?query=machine+learning&limit=10"
```

#### F. Get your user info:
```bash
curl http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Available Endpoints
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/papers/upload` - Upload PDF paper
- `GET /api/papers/search` - Search papers
- `GET /api/papers/{paper_id}` - Get paper details
- `POST /api/papers/{paper_id}/similarity` - Check for plagiarism
- `GET /api/papers/{paper_id}/analyze` - Full analysis report
- `GET /api/statistics/overview` - Platform statistics

---

## 2️⃣ API Documentation - http://localhost:8001/docs

### What It Does
**Interactive Swagger UI** for the REST API - lets you test all endpoints without writing code.

### How to Use It

1. **Open in your browser:** http://localhost:8001/docs

2. **You'll see an interactive interface with:**
   - All available API endpoints
   - Request/response schemas
   - "Try it out" buttons to test each endpoint

3. **To authenticate:**
   - Click the "Authorize" button (🔓 icon) at the top right
   - Signup first to get a token (use `/api/auth/signup` endpoint)
   - Enter your token in the format: `Bearer your-token-here`
   - Click "Authorize"
   - Now all authenticated endpoints will work!

4. **Testing an endpoint:**
   - Expand any endpoint (e.g., `POST /api/papers/upload`)
   - Click "Try it out"
   - Fill in the parameters
   - Click "Execute"
   - See the response below

**This is the easiest way to explore the API!**

---

## 3️⃣ Frontend - http://localhost:8082

### What It Does
**React web application** with a user-friendly interface for:
- Uploading research papers
- Viewing analysis results
- Searching papers
- Managing your account
- Visualizing plagiarism detection results

### How to Use It

1. **Open in your browser:** http://localhost:8082

2. **Features:**
   - **Dashboard:** Overview of recent uploads and statistics
   - **Upload:** Drag-and-drop PDF papers for analysis
   - **Search:** Find papers in the database
   - **Analysis:** View detailed reports on detected issues
   - **Profile:** Manage your account settings

3. **First Time Setup:**
   - Click "Sign Up" to create an account
   - Or "Login" if you already have one
   - Upload a PDF research paper
   - Wait for processing (runs in background via Celery)
   - View the analysis results

### Direct Frontend Access
The frontend is also available directly at: http://localhost:3000/SAGE.AI/
(This bypasses Nginx and goes straight to the Vite dev server)

---

## 4️⃣ MinIO Console - http://localhost:9001

### What It Does
**S3-compatible object storage** for storing:
- Uploaded PDF files
- Extracted images from papers
- Generated reports
- Processed data

MinIO is like Amazon S3 but running on your local machine.

### How to Use It

1. **Open in your browser:** http://localhost:9001

2. **Login credentials:**
   - Username: `minioadmin`
   - Password: `minioadmin`

3. **You'll see:**
   - **Buckets:** Containers for files (like folders)
   - **Object Browser:** View/download files
   - **Monitoring:** Storage usage statistics

4. **Expected Buckets:**
   - `papers` - Uploaded PDF files
   - `images` - Extracted figures from papers
   - `reports` - Generated analysis reports

5. **Common Tasks:**
   - **View uploaded PDFs:** Click "Buckets" → "papers"
   - **Download a file:** Click the file → "Download"
   - **Upload a file:** Click "Upload" button
   - **Delete files:** Select files → "Delete"

---

## 5️⃣ Grafana - http://localhost:4001

### What It Does
**Monitoring and visualization platform** that shows:
- System performance metrics
- API request rates
- Database query performance
- Celery worker status
- Error rates and alerts

### How to Use It

1. **Open in your browser:** http://localhost:4001

2. **Login credentials:**
   - Username: `admin`
   - Password: `admin`
   - (You'll be prompted to change this on first login)

3. **Dashboards:**
   - Navigate to "Dashboards" in the left sidebar
   - You should see pre-configured dashboards for:
     - **API Performance:** Request rates, response times
     - **Database Metrics:** Query performance, connections
     - **Worker Status:** Celery task queue metrics
     - **System Health:** CPU, memory, disk usage

4. **How to Create a Dashboard:**
   - Click "+" → "Dashboard" → "Add new panel"
   - Select data source: "Prometheus"
   - Write a query (e.g., `rate(http_requests_total[5m])`)
   - Choose visualization type (graph, gauge, table, etc.)
   - Click "Apply"

5. **Common Metrics to Monitor:**
   - `http_request_duration_seconds` - API response times
   - `celery_task_success_total` - Successfully processed papers
   - `pg_stat_database_numbackends` - Database connections
   - `redis_connected_clients` - Redis connections

---

## 6️⃣ Prometheus - http://localhost:9091

### What It Does
**Time-series database** that collects and stores metrics from all services:
- Scrapes metrics from backend API every 15 seconds
- Stores historical data for analysis
- Provides data to Grafana for visualization
- Supports alerting rules

### How to Use It

1. **Open in your browser:** http://localhost:9091

2. **Main Features:**

   **A. Query Metrics:**
   - Go to "Graph" tab
   - Enter a query in the expression box
   - Click "Execute"
   - View results as table or graph

   **B. Example Queries:**
   ```promql
   # Total HTTP requests in last 5 minutes
   rate(http_requests_total[5m])

   # Average API response time
   avg(http_request_duration_seconds)

   # Number of papers being processed
   celery_tasks{state="PROCESSING"}

   # Database connection count
   pg_stat_database_numbackends
   ```

   **C. Check Targets:**
   - Click "Status" → "Targets"
   - See all services Prometheus is monitoring
   - Green = healthy, Red = down

3. **Useful Tabs:**
   - **Graph:** Query and visualize metrics
   - **Alerts:** View active alerts (if configured)
   - **Status → Targets:** See which services are being scraped
   - **Status → Configuration:** View Prometheus config

4. **When to Use Prometheus vs Grafana:**
   - **Prometheus:** Quick ad-hoc queries, debugging, alerts
   - **Grafana:** Beautiful dashboards, long-term monitoring

---

## 🔧 Additional Services (Not Directly Accessible)

### PostgreSQL Database - port 5432 (internal)
**Purpose:** Stores all application data
- User accounts
- Paper metadata
- Analysis results
- Citations and references

**Access via command line:**
```bash
docker exec -it academic_integrity_db psql -U aiplatform -d academic_integrity
```

**Common queries:**
```sql
-- Count total papers
SELECT COUNT(*) FROM papers;

-- Count users
SELECT COUNT(*) FROM users;

-- View recent uploads
SELECT title, status, created_at FROM papers ORDER BY created_at DESC LIMIT 10;
```

### Elasticsearch - http://localhost:9200
**Purpose:** Full-text search engine for papers

**Test it:**
```bash
curl http://localhost:9200/_cluster/health?pretty
```

**Search papers:**
```bash
curl -X GET "http://localhost:9200/papers/_search?q=machine+learning"
```

### Redis - port 6379
**Purpose:**
- Celery task queue (for background processing)
- Caching layer
- Session storage

**Access via command line:**
```bash
docker exec -it academic_integrity_redis redis-cli
```

**Common commands:**
```redis
# Check number of queued tasks
LLEN celery

# View all keys
KEYS *

# Get cache statistics
INFO stats
```

### Celery Worker (ML Worker)
**Purpose:** Background processing of papers
- Runs ML models
- Extracts text from PDFs
- Performs similarity analysis
- Generates reports

**View worker logs:**
```bash
docker logs academic_integrity_ml_worker --tail 50 -f
```

### Nginx - port 8082 and 8444
**Purpose:** Reverse proxy and load balancer
- Routes traffic to frontend and backend
- Handles SSL/TLS termination (port 8444)
- Serves static files

---

## 🚀 Quick Start Workflow

Here's a complete workflow from start to finish:

### Step 1: Create an Account
```bash
# Via API
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "researcher@university.edu",
    "password": "SecurePass123",
    "full_name": "Dr. Jane Smith",
    "institution": "MIT"
  }'

# Save the token from the response!
# Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 2: Upload a Paper
```bash
# Replace YOUR_TOKEN with your actual token
curl -X POST http://localhost:8001/api/papers/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@research_paper.pdf"

# Save the paper_id from response!
```

### Step 3: Monitor Processing
```bash
# Check paper status
curl http://localhost:8001/api/papers/{paper_id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Watch Celery worker logs
docker logs academic_integrity_ml_worker -f
```

### Step 4: View Results
- Open http://localhost:8082 in browser
- Login with your credentials
- View the analysis results dashboard

### Step 5: Check for Plagiarism
```bash
curl -X POST http://localhost:8001/api/papers/{paper_id}/similarity \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "check_types": ["text", "semantic", "image"],
    "threshold": 0.3,
    "limit": 100
  }'
```

---

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check all services
docker-compose ps

# View logs for specific service
docker logs academic_integrity_backend --tail 100

# Restart a service
docker-compose restart backend
```

### Can't Connect to API
```bash
# Test if backend is responding
curl http://localhost:8001/

# Check backend logs
docker logs academic_integrity_backend --tail 50
```

### Frontend Shows Error
```bash
# Check frontend logs
docker logs academic_integrity_frontend --tail 50

# Rebuild frontend
docker-compose build frontend
docker-compose restart frontend
```

### Authentication Not Working
```bash
# Make sure JWT_SECRET is set
cat .env | grep JWT_SECRET

# Test signup endpoint
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123","full_name":"Test"}'
```

---

## 📊 Monitoring Guide

### Check System Health

1. **Backend Health:**
   ```bash
   curl http://localhost:8001/
   ```

2. **Database Health:**
   ```bash
   docker exec academic_integrity_db pg_isready
   ```

3. **Redis Health:**
   ```bash
   docker exec academic_integrity_redis redis-cli ping
   # Should return: PONG
   ```

4. **Elasticsearch Health:**
   ```bash
   curl http://localhost:9200/_cluster/health?pretty
   ```

5. **Celery Worker Status:**
   ```bash
   docker logs academic_integrity_ml_worker --tail 20 | grep "ready"
   ```

### View Metrics
- **Open Prometheus:** http://localhost:9091
- **Query:** `up{job="backend"}` (should return 1)
- **View all targets:** Status → Targets

### Create Dashboards
- **Open Grafana:** http://localhost:4001
- **Add data source:** Prometheus (http://prometheus:9090)
- **Import dashboard:** Use ID 1860 for Node Exporter dashboard

---

## 🎯 Common Use Cases

### 1. Upload and Analyze a Paper (Web UI)
1. Open http://localhost:8082
2. Click "Upload Paper"
3. Drag PDF file or click to browse
4. Wait for processing (status shows "processing")
5. View results when status changes to "completed"

### 2. Batch Upload Papers (API)
```bash
# Upload multiple papers
for file in papers/*.pdf; do
  curl -X POST http://localhost:8001/api/papers/upload \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$file"
  sleep 2
done
```

### 3. Export Analysis Results
```bash
# Get analysis for a paper
curl http://localhost:8001/api/papers/{paper_id}/analyze \
  -H "Authorization: Bearer $TOKEN" \
  > analysis_report.json
```

### 4. Monitor Processing Queue
```bash
# Check Redis queue length
docker exec academic_integrity_redis redis-cli LLEN celery

# Watch worker logs in real-time
docker logs academic_integrity_ml_worker -f
```

---

## 🔐 Security Notes

1. **Change Default Passwords:**
   - MinIO: Default is minioadmin/minioadmin
   - Grafana: Default is admin/admin

2. **JWT Tokens:**
   - Tokens expire after 30 minutes
   - Store securely (localStorage in frontend)
   - Never commit tokens to git

3. **Environment Variables:**
   - Store secrets in `.env` file
   - Never commit `.env` to version control
   - Use `.env.example` as template

4. **API Rate Limiting:**
   - Not yet implemented (on roadmap)
   - Recommended: Install slowapi

---

## 📝 Summary

**Essential Services for Daily Use:**
- **Frontend:** http://localhost:8082 (Main UI)
- **API Docs:** http://localhost:8001/docs (Test API)
- **Grafana:** http://localhost:4001 (Monitor system)

**Admin/Debug Services:**
- **MinIO:** http://localhost:9001 (View files)
- **Prometheus:** http://localhost:9091 (Query metrics)
- **Elasticsearch:** http://localhost:9200 (Search data)

**All services run in Docker containers and communicate via internal network.**

For more detailed documentation, see:
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Security analysis
- [PROJECT_COMPLETION_SUMMARY.md](PROJECT_COMPLETION_SUMMARY.md) - Technical details
- [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md) - Deployment status
