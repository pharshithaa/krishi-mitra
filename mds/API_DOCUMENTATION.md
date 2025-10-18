# 📡 Krishi Mitra API Documentation

Complete API reference for Krishi Mitra backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

---

## 🔐 Authentication Endpoints

### POST /auth/signup

Register a new farmer account.

**Request Body:**
```json
{
  "email": "farmer@example.com",
  "password": "securepass123",
  "full_name": "Rajesh Kumar",
  "phone_number": "9876543210",
  "state": "Tamil Nadu",
  "district": "Coimbatore",
  "village": "Pollachi",
  "pincode": "642001",
  "farm_size": "medium",
  "primary_crops": ["rice", "cotton", "sugarcane"]
}
```

**Response (200 OK):**
```json
{
  "message": "Farmer registration successful",
  "email": "farmer@example.com",
  "full_name": "Rajesh Kumar"
}
```

**Error Responses:**
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

### POST /auth/login

Login and receive JWT token.

**Request Body:**
```json
{
  "email": "farmer@example.com",
  "password": "securepass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `500 Internal Server Error`: Server error

---

### GET /auth/user/me

Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "email": "farmer@example.com",
  "full_name": "Rajesh Kumar",
  "phone_number": "9876543210",
  "primary_crops": ["rice", "cotton", "sugarcane"],
  "farm_size": "medium"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `404 Not Found`: User not found

---

## 🤖 RAG Endpoints

### POST /api/v1/rag/query

Main RAG endpoint for agricultural questions.

**Request Body:**
```json
{
  "query": "What is the best fertilizer for rice cultivation in kharif season?",
  "top_k": 5,
  "filters": {
    "region": "Tamil Nadu",
    "season": "kharif"
  }
}
```

**Parameters:**
- `query` (required): User's question (1-1000 characters)
- `top_k` (optional): Number of chunks to retrieve (1-20, default: 5)
- `filters` (optional): Metadata filters for retrieval

**Response (200 OK):**
```json
{
  "answer": "For rice cultivation in kharif season, NPK fertilizer with ratio 4:2:1 is recommended. Apply 120 kg of nitrogen, 60 kg of phosphorus, and 40 kg of potassium per hectare. Split nitrogen application into three doses: 50% at transplanting, 25% at tillering, and 25% at panicle initiation stage.",
  "sources": [
    {
      "source": "rice_cultivation_guide.pdf",
      "page": 15,
      "chunk_id": "chunk_123",
      "score": 0.89
    },
    {
      "source": "fertilizer_recommendations.pdf",
      "page": 8,
      "chunk_id": "chunk_456",
      "score": 0.85
    }
  ],
  "retrieved_chunks": [
    "Rice cultivation requires balanced NPK fertilization...",
    "Kharif season rice responds well to split nitrogen application..."
  ],
  "latency_ms": 2432,
  "node_latencies": {
    "embed_ms": 145.2,
    "retrieve_ms": 387.5,
    "generate_ms": 1899.3
  }
}
```

**Error Responses:**
- `422 Unprocessable Entity`: Invalid query format
- `500 Internal Server Error`: Pipeline execution failed

**Performance:**
- Average latency: 2-5 seconds
- Embedding: ~150ms
- Retrieval: ~400ms
- Generation: ~2s

---

### POST /api/v1/rag/embed

Generate embeddings for text (debugging/testing).

**Request Body:**
```json
{
  "text": "What crops are suitable for kharif season?"
}
```

**Response (200 OK):**
```json
{
  "embeddings": [0.123, -0.456, 0.789, ...],  // 768 dimensions
  "dimension": 768,
  "processing_time_ms": 145.2
}
```

**Use Cases:**
- Testing embedding service
- Debugging similarity issues
- Pre-computing embeddings

---

### GET /api/v1/rag/health

Health check for all RAG services.

**Response (200 OK):**
```json
{
  "status": "ok",
  "pinecone": "connected",
  "langgraph": "running",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "details": {
    "retrieval": {
      "status": "connected",
      "pinecone_index": "krishimitra-knowledge",
      "total_vectors": 10000
    },
    "pipeline": {
      "status": "running",
      "nodes": ["embed", "retrieve", "generate"],
      "graph_compiled": true
    },
    "generation": {
      "status": "running",
      "provider": "gemini",
      "model": "gemini-2.0-flash-exp"
    }
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "degraded",
  "pinecone": "disconnected",
  "langgraph": "running",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "details": {
    "retrieval": {
      "status": "disconnected",
      "error": "Connection timeout"
    }
  }
}
```

**Status Values:**
- `ok`: All services operational
- `degraded`: Some services down
- `error`: Critical failure

---

### GET /api/v1/rag/graph/visualize

Get LangGraph workflow structure.

**Response (200 OK):**
```json
{
  "nodes": [
    {
      "id": "embed",
      "name": "EmbedNode",
      "type": "embedding"
    },
    {
      "id": "retrieve",
      "name": "RetrieveNode",
      "type": "retrieval"
    },
    {
      "id": "generate",
      "name": "GenerateNode",
      "type": "generation"
    }
  ],
  "edges": [
    {
      "source": "START",
      "target": "embed",
      "condition": null
    },
    {
      "source": "embed",
      "target": "retrieve",
      "condition": null
    },
    {
      "source": "retrieve",
      "target": "generate",
      "condition": null
    },
    {
      "source": "generate",
      "target": "END",
      "condition": null
    }
  ],
  "entry_point": "embed",
  "description": "LangGraph-orchestrated RAG pipeline: Embed -> Retrieve -> Generate"
}
```

**Use Cases:**
- Debugging pipeline flow
- Visualizing workflow
- Understanding architecture

---

## 📊 Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing or invalid token |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service down |

---

## 🔧 Rate Limiting

Currently no rate limiting implemented. Recommended for production:
- 100 requests/minute per user
- 1000 requests/hour per IP

---

## 📝 Example Usage

### Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "farmer@example.com", "password": "pass123"}
)
token = response.json()["access_token"]

# Query RAG
response = requests.post(
    "http://localhost:8000/api/v1/rag/query",
    json={"query": "Best fertilizer for rice?", "top_k": 5}
)
print(response.json()["answer"])
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'farmer@example.com',
    password: 'pass123'
  })
});
const {access_token} = await loginResponse.json();

// Query RAG
const ragResponse = await fetch('http://localhost:8000/api/v1/rag/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: 'Best fertilizer for rice?',
    top_k: 5
  })
});
const {answer} = await ragResponse.json();
console.log(answer);
```

### cURL

```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer@example.com","password":"pass123"}' \
  | jq -r '.access_token')

# Query RAG
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Best fertilizer for rice?","top_k":5}'
```

---

## 🔍 Error Handling

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

For RAG-specific errors:

```json
{
  "error": "Pipeline execution failed",
  "detail": "Embedding failed: Connection timeout",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## 📈 Performance Tips

1. **Optimize top_k**: Use 3-5 for faster responses
2. **Use filters**: Narrow down search space
3. **Cache results**: Cache frequent queries
4. **Batch requests**: Group similar queries
5. **Monitor latency**: Use node_latencies for debugging

---

**API Version:** 2.0.0  
**Last Updated:** January 2025
