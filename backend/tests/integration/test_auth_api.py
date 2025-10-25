"""
Integration tests for authentication API
Tests: backend/routers/auth.py
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthenticationAPI:
    """Test authentication endpoints"""
    
    def test_signup_success(self, test_client, test_user_data):
        """Test successful user signup"""
        response = test_client.post("/auth/signup", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "password" not in data  # Password should not be returned
    
    def test_signup_duplicate_email(self, test_client, test_user_data):
        """Test signup with duplicate email"""
        # First signup
        test_client.post("/auth/signup", json=test_user_data)
        
        # Second signup with same email
        response = test_client.post("/auth/signup", json=test_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_signup_invalid_farm_size(self, test_client, test_user_data):
        """Test signup with invalid farm size"""
        invalid_data = test_user_data.copy()
        invalid_data["farm_size"] = "extra_large"  # Invalid enum value
        
        response = test_client.post("/auth/signup", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_signup_missing_required_fields(self, test_client):
        """Test signup with missing required fields"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing other required fields
        }
        
        response = test_client.post("/auth/signup", json=incomplete_data)
        
        assert response.status_code == 422
    
    def test_login_success(self, test_client, test_user_data):
        """Test successful login"""
        # First create user
        test_client.post("/auth/signup", json=test_user_data)
        
        # Then login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_wrong_password(self, test_client, test_user_data):
        """Test login with wrong password"""
        # Create user
        test_client.post("/auth/signup", json=test_user_data)
        
        # Login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, test_client):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_get_user_info_authenticated(self, test_client, test_user_data):
        """Test getting user info with valid token"""
        # Signup and login
        test_client.post("/auth/signup", json=test_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Get user info
        response = test_client.get(
            "/auth/user/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "password" not in data
    
    def test_get_user_info_no_token(self, test_client):
        """Test getting user info without token"""
        response = test_client.get("/auth/user/me")
        
        assert response.status_code == 403  # Forbidden
    
    def test_get_user_info_invalid_token(self, test_client):
        """Test getting user info with invalid token"""
        response = test_client.get(
            "/auth/user/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


# Expected Results:
# - All tests should pass
# - Test coverage for auth.py: ~85%
# - Execution time: < 5 seconds
# - Validates: signup, login, token generation, protected routes
# - Tests both success and failure scenarios
