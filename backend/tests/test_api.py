"""
Unit tests for API endpoints
backend/tests/test_api.py
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, Base, get_db

# Test database - Use PostgreSQL UUID type with special handling
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Patch UUID type for SQLite compatibility
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

class UUID(TypeDecorator):
    """Platform-independent UUID type - uses CHAR(32) for SQLite"""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

# Monkey patch UUID in main module
import main
main.UUID = UUID

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create and drop database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestRootEndpoint:
    """Test root API endpoint"""

    def test_root_returns_200(self):
        """Test that root endpoint returns 200"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_has_platform_info(self):
        """Test that root endpoint returns platform info"""
        response = client.get("/")
        data = response.json()

        assert "platform" in data
        assert "version" in data
        assert "endpoints" in data


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_signup_success(self):
        """Test successful user signup"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
                "full_name": "Test User",
                "institution": "Test University"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["full_name"] == "Test User"
        assert data["user"]["role"] == "user"

    def test_signup_weak_password(self):
        """Test signup with weak password"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "weak",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 400
        assert "Password must be at least 8 characters" in response.json()["detail"]

    def test_signup_duplicate_email(self):
        """Test signup with duplicate email"""
        # First signup
        client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
                "full_name": "Test User"
            }
        )

        # Try to signup again with same email
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
                "full_name": "Another User"
            }
        )

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_login_success(self):
        """Test successful login"""
        # First create user
        client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
                "full_name": "Test User"
            }
        )

        # Then login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        assert data["user"]["email"] == "test@example.com"

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Create user
        client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
                "full_name": "Test User"
            }
        )

        # Try to login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword"
            }
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self):
        """Test login with non-existent email"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPass123"
            }
        )

        assert response.status_code == 401

    def test_me_endpoint_with_valid_token(self):
        """Test /me endpoint with valid token"""
        # Signup and get token
        signup_response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
                "full_name": "Test User",
                "institution": "Test Uni"
            }
        )
        token = signup_response.json()["access_token"]

        # Call /me endpoint
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["role"] == "user"
        assert data["institution"] == "Test Uni"
        assert data["is_active"] is True

    def test_me_endpoint_without_token(self):
        """Test /me endpoint without token"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403

    def test_me_endpoint_with_invalid_token(self):
        """Test /me endpoint with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 403


class TestStatisticsEndpoint:
    """Test statistics endpoint"""

    def test_statistics_overview(self):
        """Test statistics overview endpoint"""
        response = client.get("/api/statistics/overview")
        assert response.status_code == 200

        data = response.json()
        assert "total_papers" in data
        assert "papers_flagged" in data
        assert "avg_similarity_score" in data
        assert isinstance(data["total_papers"], int)


class TestPaperSearch:
    """Test paper search endpoint"""

    def test_paper_search(self):
        """Test paper search with no papers"""
        response = client.get("/api/papers/search")
        assert response.status_code == 200

        data = response.json()
        assert "papers" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["papers"]) == 0

    def test_paper_search_with_limit(self):
        """Test paper search with limit parameter"""
        response = client.get("/api/papers/search?limit=10")
        assert response.status_code == 200

        data = response.json()
        assert "papers" in data
        assert "total" in data
