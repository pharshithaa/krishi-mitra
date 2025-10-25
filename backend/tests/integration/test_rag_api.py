"""
Integration tests for RAG API
Tests: backend/routers/rag.py
"""
import pytest
from unittest.mock import patch, MagicMock


class TestRAGAPI:
    """Test RAG endpoints"""
    
    @patch('services.langgraph_pipeline.rag_pipeline')
    def test_query_endpoint_success(self, mock_pipeline, test_client, sample_query):
        """Test successful RAG query"""
        # Mock the pipeline response
        mock_pipeline.run.return_value = {
            "answer": "For rice cultivation, use NPK fertilizer at 120:60:40 kg/ha.",
            "sources": [{"source": "test.pdf", "score": 0.85}],
            "retrieved_chunks": [{"text": "Test content", "score": 0.85}],
            "latency_ms": 2000,
            "node_latencies": {
                "embed_ms": 50,
                "retrieve_ms": 800,
                "generate_ms": 1150
            }
        }
        
        response = test_client.post(
            "/api/v1/rag/query",
            json={"query": sample_query, "top_k": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "retrieved_chunks" in data
        assert "latency_ms" in data
        assert data["latency_ms"] > 0
    
    @patch('services.langgraph_pipeline.rag_pipeline')
    def test_query_endpoint_with_filters(self, mock_pipeline, test_client):
        """Test RAG query with metadata filters"""
        mock_pipeline.run.return_value = {
            "answer": "Test answer",
            "sources": [],
            "retrieved_chunks": [],
            "latency_ms": 1500
        }
        
        response = test_client.post(
            "/api/v1/rag/query",
            json={
                "query": "What crops grow in Punjab?",
                "top_k": 3,
                "filters": {"state": "Punjab"}
            }
        )
        
        assert response.status_code == 200
        # Verify filters were passed to pipeline
        mock_pipeline.run.assert_called_once()
        call_args = mock_pipeline.run.call_args
        assert call_args[1]["filters"] == {"state": "Punjab"}
    
    @patch('services.langgraph_pipeline.rag_pipeline')
    def test_query_endpoint_empty_query(self, mock_pipeline, test_client):
        """Test RAG query with empty string"""
        response = test_client.post(
            "/api/v1/rag/query",
            json={"query": "", "top_k": 5}
        )
        
        # Should either return 422 (validation error) or handle gracefully
        assert response.status_code in [200, 422]
    
    @patch('services.langgraph_pipeline.rag_pipeline')
    def test_query_endpoint_pipeline_error(self, mock_pipeline, test_client):
        """Test RAG query when pipeline fails"""
        mock_pipeline.run.side_effect = Exception("Pipeline error")
        
        response = test_client.post(
            "/api/v1/rag/query",
            json={"query": "Test query", "top_k": 5}
        )
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()
    
    @patch('services.embeddings.embedding_service')
    def test_embed_endpoint_success(self, mock_embedding, test_client):
        """Test embedding endpoint"""
        mock_embedding.embed_query.return_value = ([0.1] * 768, 50.0)
        
        response = test_client.post(
            "/api/v1/rag/embed",
            json={"text": "Test text for embedding"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "embeddings" in data
        assert "dimension" in data
        assert "processing_time_ms" in data
        assert data["dimension"] == 768
    
    @patch('services.retrieval.retrieval_service')
    @patch('services.langgraph_pipeline.rag_pipeline')
    @patch('services.generation.generation_service')
    def test_health_endpoint_all_healthy(
        self, mock_gen, mock_pipeline, mock_retrieval, test_client
    ):
        """Test health check when all services are healthy"""
        mock_retrieval.health_check.return_value = {
            "status": "connected",
            "total_vectors": 1000
        }
        mock_pipeline.health_check.return_value = {
            "status": "running"
        }
        mock_gen.health_check.return_value = {
            "status": "running",
            "provider": "gemini",
            "model": "gemini-1.5-flash"
        }
        
        response = test_client.get("/api/v1/rag/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["pinecone"] == "connected"
        assert data["langgraph"] == "running"
    
    @patch('services.retrieval.retrieval_service')
    def test_health_endpoint_service_down(self, mock_retrieval, test_client):
        """Test health check when a service is down"""
        mock_retrieval.health_check.return_value = {
            "status": "error"
        }
        
        response = test_client.get("/api/v1/rag/health")
        
        assert response.status_code == 503  # Service Unavailable
    
    @patch('services.langgraph_pipeline.rag_pipeline')
    def test_graph_visualization_endpoint(self, mock_pipeline, test_client):
        """Test graph visualization endpoint"""
        mock_pipeline.get_graph_structure.return_value = {
            "nodes": ["EmbedNode", "RetrieveNode", "GenerateNode"],
            "edges": [("EmbedNode", "RetrieveNode"), ("RetrieveNode", "GenerateNode")],
            "entry_point": "EmbedNode",
            "description": "RAG Pipeline"
        }
        
        response = test_client.get("/api/v1/rag/graph/visualize")
        
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 3


# Expected Results:
# - All tests should pass
# - Test coverage for rag.py: ~80%
# - Execution time: < 3 seconds
# - Validates: query endpoint, embedding endpoint, health check, error handling
# - Tests with mocked services to avoid external dependencies
