"""
RAG API routes for Krishi Mitra
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from schemas.rag import (
    QueryRequest, QueryResponse, EmbedRequest, EmbedResponse,
    HealthResponse, GraphVisualization, ErrorResponse
)
from services.langgraph_pipeline import rag_pipeline
from services.embeddings import embedding_service
from services.retrieval import retrieval_service
from services.generation import generation_service
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Main RAG endpoint: LangGraph-orchestrated retrieval and generation
    
    This endpoint processes agricultural queries using a three-stage pipeline:
    1. EmbedNode: Converts query to vector embedding
    2. RetrieveNode: Fetches relevant chunks from Pinecone
    3. GenerateNode: Generates answer using Gemini LLM
    """
    try:
        logger.info(f"Processing query via LangGraph: {request.query[:100]}...")
        
        # Execute LangGraph pipeline
        result = rag_pipeline.run(
            query=request.query,
            top_k=request.top_k or 5,
            filters=request.filters
        )
        
        # Prepare response
        response = QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            retrieved_chunks=result["retrieved_chunks"],
            latency_ms=result["latency_ms"],
            node_latencies=result.get("node_latencies")
        )
        
        logger.info(f"Query processed successfully in {result['latency_ms']}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/embed", response_model=EmbedResponse)
async def embed_endpoint(request: EmbedRequest):
    """
    Generate embeddings for input text (for testing/debugging)
    """
    try:
        # Generate embeddings
        embeddings, processing_time_ms = embedding_service.embed_query(request.text)
        
        response = EmbedResponse(
            embeddings=embeddings,
            dimension=len(embeddings),
            processing_time_ms=processing_time_ms
        )
        
        logger.info(f"Generated embeddings for text in {processing_time_ms}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embeddings: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_endpoint():
    """
    Health check endpoint for all RAG services
    
    Checks:
    - Pinecone connection and index status
    - LangGraph pipeline status
    - LLM service availability
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        
        # Check Pinecone connection
        retrieval_health = await retrieval_service.health_check()
        pinecone_status = retrieval_health.get("status", "unknown")
        
        # Check LangGraph pipeline
        pipeline_health = rag_pipeline.health_check()
        langgraph_status = pipeline_health.get("status", "unknown")
        
        # Check LLM service
        generation_health = generation_service.health_check()
        
        # Determine overall status
        overall_status = "ok" if (pinecone_status == "connected" and langgraph_status == "running") else "degraded"
        
        response = HealthResponse(
            status=overall_status,
            pinecone=pinecone_status,
            langgraph=langgraph_status,
            timestamp=timestamp,
            details={
                "retrieval": retrieval_health,
                "pipeline": pipeline_health,
                "generation": generation_health
            }
        )
        
        if overall_status != "ok":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=response.dict()
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        error_response = ErrorResponse(
            error="Health check failed",
            detail=str(e),
            timestamp=datetime.utcnow().isoformat()
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response.dict()
        )


@router.get("/graph/visualize", response_model=GraphVisualization)
async def visualize_graph_endpoint():
    """
    Get LangGraph workflow structure for visualization
    
    Returns the nodes and edges of the RAG pipeline for debugging
    and visualization purposes.
    """
    try:
        graph_structure = rag_pipeline.get_graph_structure()
        
        response = GraphVisualization(
            nodes=graph_structure["nodes"],
            edges=graph_structure["edges"],
            entry_point=graph_structure["entry_point"],
            description=graph_structure["description"]
        )
        
        logger.info("Graph structure retrieved successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error getting graph structure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting graph structure: {str(e)}"
        )
