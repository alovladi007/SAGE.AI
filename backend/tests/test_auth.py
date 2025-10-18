"""
Unit tests for authentication module
backend/tests/test_auth.py
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt

from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    validate_password_strength,
    SECRET_KEY,
    ALGORITHM
)


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_password_hash_and_verify(self):
        """Test that password hashing and verification works"""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        # Hash should not equal plain password
        assert hashed != password

        # Verification should succeed with correct password
        assert verify_password(password, hashed) is True

        # Verification should fail with wrong password
        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)"""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestPasswordValidation:
    """Test password strength validation"""

    def test_valid_password(self):
        """Test that valid passwords pass validation"""
        valid_passwords = [
            "Password123",
            "Test1234",
            "MySecure99",
            "Admin2023"
        ]

        for password in valid_passwords:
            is_valid, error = validate_password_strength(password)
            assert is_valid is True
            assert error is None

    def test_too_short(self):
        """Test that short passwords are rejected"""
        is_valid, error = validate_password_strength("Pass1")
        assert is_valid is False
        assert "at least 8 characters" in error

    def test_missing_uppercase(self):
        """Test that passwords without uppercase are rejected"""
        is_valid, error = validate_password_strength("password123")
        assert is_valid is False
        assert "uppercase" in error

    def test_missing_lowercase(self):
        """Test that passwords without lowercase are rejected"""
        is_valid, error = validate_password_strength("PASSWORD123")
        assert is_valid is False
        assert "lowercase" in error

    def test_missing_digit(self):
        """Test that passwords without digits are rejected"""
        is_valid, error = validate_password_strength("PasswordABC")
        assert is_valid is False
        assert "digit" in error


class TestJWTTokens:
    """Test JWT token creation and validation"""

    def test_create_and_decode_token(self):
        """Test token creation and decoding"""
        data = {
            "sub": "user123",
            "email": "test@example.com",
            "role": "user"
        }

        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode token
        token_data = decode_access_token(token)
        assert token_data.user_id == "user123"
        assert token_data.email == "test@example.com"
        assert token_data.role == "user"

    def test_token_expiration(self):
        """Test that tokens have correct expiration"""
        data = {"sub": "user123", "email": "test@example.com"}
        expires_delta = timedelta(minutes=15)

        token = create_access_token(data, expires_delta=expires_delta)

        # Manually decode to check expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.utcfromtimestamp(payload["exp"])
        now = datetime.utcnow()

        # Expiration should be approximately 15 minutes from now
        delta = exp - now
        assert 14 * 60 < delta.total_seconds() < 16 * 60

    def test_invalid_token(self):
        """Test that invalid tokens are rejected"""
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")

        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in str(exc_info.value.detail)

    def test_token_without_user_id(self):
        """Test that tokens without user_id are rejected"""
        # Create token without 'sub' field
        payload = {"email": "test@example.com", "role": "user"}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)

        assert exc_info.value.status_code == 401


class TestTokenData:
    """Test TokenData model"""

    def test_token_data_creation(self):
        """Test creating TokenData objects"""
        from auth import TokenData

        token_data = TokenData(
            user_id="user123",
            email="test@example.com",
            role="admin"
        )

        assert token_data.user_id == "user123"
        assert token_data.email == "test@example.com"
        assert token_data.role == "admin"

    def test_token_data_optional_fields(self):
        """Test TokenData with optional fields"""
        from auth import TokenData

        token_data = TokenData()
        assert token_data.user_id is None
        assert token_data.email is None
        assert token_data.role is None
