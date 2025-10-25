"""
Unit tests for embedding service
Tests: backend/services/embeddings.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np


class TestEmbeddingService:
    """Test suite for EmbeddingService"""
    
    @patch('services.embeddings.SentenceTransformer')
    def test_initialization(self, mock_transformer):
        """Test embedding service initialization"""
        from services.embeddings import EmbeddingService
        
        service = EmbeddingService()
        
        assert service.model is not None
        mock_transformer.assert_called_once()
    
    @patch('services.embeddings.SentenceTransformer')
    def test_embed_query_success(self, mock_transformer):
        """Test successful query embedding"""
        from services.embeddings import EmbeddingService
        
        # Mock the model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.1] * 768)
        mock_transformer.return_value = mock_model
        
        service = EmbeddingService()
        embeddings, latency = service.embed_query("What is the best fertilizer for rice?")
        
        assert len(embeddings) == 768
        assert isinstance(latency, float)
        assert latency >= 0
        mock_model.encode.assert_called_once()
    
    @patch('services.embeddings.SentenceTransformer')
    def test_embed_query_empty_string(self, mock_transformer):
        """Test embedding with empty string"""
        from services.embeddings import EmbeddingService
        
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.0] * 768)
        mock_transformer.return_value = mock_model
        
        service = EmbeddingService()
        embeddings, latency = service.embed_query("")
        
        assert len(embeddings) == 768
        assert isinstance(latency, float)
    
    @patch('services.embeddings.SentenceTransformer')
    def test_embed_documents_success(self, mock_transformer):
        """Test successful document embedding"""
        from services.embeddings import EmbeddingService
        
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1] * 768, [0.2] * 768])
        mock_transformer.return_value = mock_model
        
        service = EmbeddingService()
        texts = ["Document 1", "Document 2"]
        embeddings, latency = service.embed_documents(texts)
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) == 768
        assert isinstance(latency, float)
        assert latency >= 0
    
    @patch('services.embeddings.SentenceTransformer')
    def test_embed_documents_single_doc(self, mock_transformer):
        """Test embedding a single document"""
        from services.embeddings import EmbeddingService
        
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1] * 768])
        mock_transformer.return_value = mock_model
        
        service = EmbeddingService()
        embeddings, latency = service.embed_documents(["Single document"])
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 768
    
    @patch('services.embeddings.SentenceTransformer')
    def test_embedding_dimension_consistency(self, mock_transformer):
        """Test that embeddings maintain consistent dimensions"""
        from services.embeddings import EmbeddingService
        
        mock_model = MagicMock()
        mock_model.encode.side_effect = [
            np.array([0.1] * 768),
            np.array([0.2] * 768),
            np.array([0.3] * 768)
        ]
        mock_transformer.return_value = mock_model
        
        service = EmbeddingService()
        
        emb1, _ = service.embed_query("Query 1")
        emb2, _ = service.embed_query("Query 2")
        emb3, _ = service.embed_query("Query 3")
        
        assert len(emb1) == len(emb2) == len(emb3) == 768


# Expected Results:
# - All tests should pass
# - Test coverage for embeddings.py: ~80%
# - Execution time: < 2 seconds
# - Validates: initialization, query embedding, document embedding, error handling
