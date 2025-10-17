#!/bin/bash
# Deployment Verification Script for SAGE.AI
# Tests all critical functionality end-to-end

set -e

BASE_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:8082"

echo "=================================="
echo "SAGE.AI Deployment Verification"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Test 1: Backend API Health
echo "Test 1: Backend API Health Check"
response=$(curl -s $BASE_URL/)
if echo "$response" | grep -q "Academic Integrity Platform"; then
    pass "Backend API is responding"
else
    fail "Backend API is not responding correctly"
fi

# Test 2: Statistics Endpoint
echo "Test 2: Statistics Endpoint"
stats=$(curl -s $BASE_URL/api/statistics/overview)
if echo "$stats" | grep -q "total_papers"; then
    pass "Statistics endpoint working"
else
    fail "Statistics endpoint not working"
fi

# Test 3: Database Connection
echo "Test 3: Database Connection"
if echo "$stats" | python3 -c "import sys, json; data=json.load(sys.stdin); sys.exit(0 if 'total_papers' in data else 1)"; then
    pass "Database connection working"
else
    fail "Database connection issue"
fi

# Test 4: Search Endpoint
echo "Test 4: Paper Search Endpoint"
search=$(curl -s "$BASE_URL/api/papers/search?limit=5")
if echo "$search" | grep -q "total"; then
    pass "Search endpoint working"
    papers=$(echo "$search" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])")
    echo "   Found $papers papers in database"
else
    fail "Search endpoint not working"
fi

# Test 5: File Upload
echo "Test 5: File Upload"
cat > /tmp/test_upload.txt << 'TESTEOF'
Title: Test Paper for Deployment Verification
Abstract: This is a test paper to verify the upload functionality works correctly.
Content: Academic integrity is important. This paper tests the system.
TESTEOF

upload_result=$(curl -s -X POST $BASE_URL/api/papers/upload \
    -F "file=@/tmp/test_upload.txt" \
    -F 'metadata={"title":"Deployment Test Paper","authors":["Test Author"]}')

if echo "$upload_result" | grep -q "paper_id"; then
    paper_id=$(echo "$upload_result" | python3 -c "import sys, json; print(json.load(sys.stdin)['paper_id'])")
    if [ "$paper_id" != "" ]; then
        pass "File upload working (Paper ID: ${paper_id:0:8}...)"
    else
        fail "Paper ID not returned"
    fi
else
    # Check if duplicate
    if echo "$upload_result" | grep -q "duplicate"; then
        pass "File upload working (duplicate detected)"
    else
        fail "File upload not working"
    fi
fi

# Test 6: Docker Services
echo "Test 6: Docker Services Status"
services=("postgres" "redis" "backend" "frontend" "nginx" "elasticsearch" "minio")
all_running=true

for service in "${services[@]}"; do
    if docker-compose ps | grep "$service" | grep -q "Up"; then
        echo "   ✓ $service is running"
    else
        echo "   ✗ $service is NOT running"
        all_running=false
    fi
done

if [ "$all_running" = true ]; then
    pass "All critical services are running"
else
    warn "Some services are not running"
fi

# Test 7: Frontend Accessibility
echo "Test 7: Frontend Accessibility"
if curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL | grep -q "200"; then
    pass "Frontend is accessible"
else
    warn "Frontend may not be accessible at $FRONTEND_URL"
fi

# Test 8: API Documentation
echo "Test 8: API Documentation (Swagger)"
if curl -s "$BASE_URL/docs" | grep -q "swagger\|openapi\|redoc"; then
    pass "API documentation is available at $BASE_URL/docs"
else
    warn "API documentation may not be available"
fi

# Summary
echo ""
echo "=================================="
echo "Deployment Verification Complete"
echo "=================================="
echo ""
echo "✓ Backend API: $BASE_URL"
echo "✓ API Docs: $BASE_URL/docs"
echo "✓ Frontend: $FRONTEND_URL"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "=================================="
