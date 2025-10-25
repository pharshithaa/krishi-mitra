"""
Unit tests for security functions
Tests: backend/core/security.py
"""
import pytest
from datetime import datetime, timedelta


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        from core.security import hash_password
        
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_hash_password_different_outputs(self):
        """Test that same password produces different hashes (salt)"""
        from core.security import hash_password
        
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different due to salt
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        from core.security import hash_password, verify_password
        
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        from core.security import hash_password, verify_password
        
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """Test password verification with empty password"""
        from core.security import hash_password, verify_password
        
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Test JWT token functions"""
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        from core.security import create_access_token
        
        data = {"email": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2  # JWT format: header.payload.signature
    
    def test_decode_access_token_valid(self):
        """Test decoding valid JWT token"""
        from core.security import create_access_token, decode_access_token
        
        data = {"email": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["email"] == "test@example.com"
        assert decoded["user_id"] == "123"
        assert "exp" in decoded  # Expiration time
    
    def test_decode_access_token_invalid(self):
        """Test decoding invalid JWT token"""
        from core.security import decode_access_token
        
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
    
    def test_decode_access_token_expired(self):
        """Test decoding expired JWT token"""
        from core.security import create_access_token, decode_access_token
        import jwt
        from core.config import get_settings
        
        settings = get_settings()
        
        # Create token that expired 1 hour ago
        data = {"email": "test@example.com"}
        expired_time = datetime.utcnow() - timedelta(hours=1)
        
        token = jwt.encode(
            {**data, "exp": expired_time},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        decoded = decode_access_token(token)
        
        assert decoded is None  # Should return None for expired token
    
    def test_token_contains_expiration(self):
        """Test that token contains expiration time"""
        from core.security import create_access_token, decode_access_token
        
        data = {"email": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert "exp" in decoded
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        
        # Token should expire in the future
        assert exp_time > now


# Expected Results:
# - All tests should pass
# - Test coverage for security.py: ~90%
# - Execution time: < 1 second
# - Validates: password hashing, verification, JWT creation, decoding, expiration
