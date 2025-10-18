#!/usr/bin/env python3
"""
Quick test script for RAG pipeline
Run this to verify your RAG setup is working correctly
"""
import sys
import requests
from typing import Dict, Any


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def test_server_running(base_url: str) -> bool:
    """Test if server is running"""
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print_success("Server is running")
            data = response.json()
            print_info(f"Version: {data.get('version', 'unknown')}")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server")
        print_info("Make sure server is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_health_check(base_url: str) -> bool:
    """Test RAG health check"""
    try:
        response = requests.get(f"{base_url}/api/v1/rag/health", timeout=10)
        data = response.json()
        
        print_info("Health Check Results:")
        print(f"  Overall Status: {data.get('status', 'unknown')}")
        print(f"  Pinecone: {data.get('pinecone', 'unknown')}")
        print(f"  LangGraph: {data.get('langgraph', 'unknown')}")
        
        if response.status_code == 200 and data.get('status') == 'ok':
            print_success("All RAG services are healthy")
            
            # Print details
            details = data.get('details', {})
            if 'retrieval' in details:
                retrieval = details['retrieval']
                print_info(f"  Pinecone vectors: {retrieval.get('total_vectors', 'unknown')}")
            
            if 'generation' in details:
                generation = details['generation']
                print_info(f"  LLM provider: {generation.get('provider', 'unknown')}")
                print_info(f"  LLM model: {generation.get('model', 'unknown')}")
            
            return True
        else:
            print_warning("Some services are not healthy")
            return False
            
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_embedding(base_url: str) -> bool:
    """Test embedding service"""
    try:
        response = requests.post(
            f"{base_url}/api/v1/rag/embed",
            json={"text": "What is the best fertilizer for rice?"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Embedding service working")
            print_info(f"  Dimension: {data.get('dimension', 'unknown')}")
            print_info(f"  Processing time: {data.get('processing_time_ms', 0):.2f}ms")
            return True
        else:
            print_error(f"Embedding failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Embedding test failed: {e}")
        return False


def test_rag_query(base_url: str) -> bool:
    """Test RAG query"""
    try:
        print_info("Testing RAG query (this may take a few seconds)...")
        
        response = requests.post(
            f"{base_url}/api/v1/rag/query",
            json={
                "query": "What is the best fertilizer for rice cultivation?",
                "top_k": 3
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("RAG query successful")
            
            print(f"\n{Colors.BOLD}Query:{Colors.END} What is the best fertilizer for rice cultivation?")
            print(f"\n{Colors.BOLD}Answer:{Colors.END}")
            print(f"{data.get('answer', 'No answer')}\n")
            
            print_info("Performance Metrics:")
            print(f"  Total latency: {data.get('latency_ms', 0)}ms")
            
            node_latencies = data.get('node_latencies', {})
            if node_latencies:
                print(f"  Embed: {node_latencies.get('embed_ms', 0):.2f}ms")
                print(f"  Retrieve: {node_latencies.get('retrieve_ms', 0):.2f}ms")
                print(f"  Generate: {node_latencies.get('generate_ms', 0):.2f}ms")
            
            sources = data.get('sources', [])
            if sources:
                print_info(f"Sources: {len(sources)} documents")
                for i, source in enumerate(sources[:3], 1):
                    print(f"  {i}. {source.get('source', 'unknown')} (score: {source.get('score', 0):.3f})")
            
            return True
        else:
            print_error(f"RAG query failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("RAG query timed out (>60s)")
        print_warning("This might indicate an issue with Pinecone or Gemini API")
        return False
    except Exception as e:
        print_error(f"RAG query test failed: {e}")
        return False


def test_graph_visualization(base_url: str) -> bool:
    """Test graph visualization"""
    try:
        response = requests.get(f"{base_url}/api/v1/rag/graph/visualize", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Graph visualization working")
            print_info(f"  Pipeline: {data.get('description', 'unknown')}")
            print_info(f"  Nodes: {len(data.get('nodes', []))}")
            print_info(f"  Edges: {len(data.get('edges', []))}")
            return True
        else:
            print_error(f"Graph visualization failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Graph visualization test failed: {e}")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}🌾 Krishi Mitra RAG Pipeline Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    base_url = "http://localhost:8001"
    
    tests = [
        ("Server Running", lambda: test_server_running(base_url)),
        ("Health Check", lambda: test_health_check(base_url)),
        ("Embedding Service", lambda: test_embedding(base_url)),
        ("Graph Visualization", lambda: test_graph_visualization(base_url)),
        ("RAG Query (Full Pipeline)", lambda: test_rag_query(base_url)),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{Colors.BOLD}Testing: {test_name}{Colors.END}")
        print("-" * 60)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print_success("\nAll tests passed! Your RAG pipeline is working correctly. 🎉")
        return 0
    else:
        print_warning(f"\n{total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
