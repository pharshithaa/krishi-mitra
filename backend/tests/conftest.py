"""
Pytest configuration and fixtures for Krishi Mitra backend tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service"""
    mock = Mock()
    mock.embed_query.return_value = ([0.1] * 768, 50.0)  # embeddings, latency
    mock.embed_documents.return_value = ([[0.1] * 768], 100.0)
    return mock


@pytest.fixture
def mock_retrieval_service():
    """Mock retrieval service"""
    mock = Mock()
    mock.search.return_value = (
        [
            {
                "id": "test-chunk-1",
                "text": "Test agricultural content about rice",
                "score": 0.85,
                "metadata": {"filename": "test.pdf", "state": "Punjab", "crop": "Rice"}
            }
        ],
        200.0  # latency
    )
    return mock


@pytest.fixture
def mock_generation_service():
    """Mock generation service"""
    mock = Mock()
    mock.generate_answer.return_value = (
        "This is a test answer about rice cultivation.",
        500.0  # latency
    )
    return mock


@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return "What is the best fertilizer for rice?"


@pytest.fixture
def sample_chunks():
    """Sample retrieved chunks for testing"""
    return [
        {
            "id": "chunk-1",
            "text": "For rice cultivation, use NPK fertilizer at 120:60:40 kg/ha.",
            "score": 0.85,
            "metadata": {"filename": "rice_guide.pdf", "state": "Punjab", "crop": "Rice"}
        },
        {
            "id": "chunk-2",
            "text": "Apply urea in split doses for better nitrogen uptake.",
            "score": 0.78,
            "metadata": {"filename": "fertilizer_guide.pdf", "state": "Punjab", "crop": "Rice"}
        }
    ]


@pytest.fixture
def test_user_data():
    """Sample user data for authentication tests"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "farm_size": "medium",
        "primary_crops": ["rice", "wheat"]
    }
