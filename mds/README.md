# 🌾 Krishi Mitra - AI-Powered Agricultural Assistant

A comprehensive agricultural platform combining user authentication with an intelligent RAG (Retrieval-Augmented Generation) system powered by LangGraph, Pinecone, and Gemini AI.

## 🎯 Features

- **User Authentication**: Secure farmer registration and login with JWT tokens
- **AI RAG Assistant**: LangGraph-orchestrated pipeline for intelligent agricultural advice
- **Vector Search**: Pinecone-powered semantic search over agricultural documents
- **LLM Generation**: Gemini 2.0 Flash for contextual answer generation
- **MongoDB Integration**: User data and farm information storage
- **RESTful API**: FastAPI-based backend with comprehensive endpoints

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Krishi Mitra Backend                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐      ┌──────────────────┐   │
│  │     Auth     │      │   RAG Pipeline   │   │
│  │   System     │      │   (LangGraph)    │   │
│  └──────────────┘      └──────────────────┘   │
│         │                       │              │
│         │                       │              │
│    ┌────▼────┐      ┌───────────▼──────────┐  │
│    │ MongoDB │      │  Embed → Retrieve    │  │
│    │  Users  │      │       → Generate     │  │
│    └─────────┘      └──────────────────────┘  │
│                              │                 │
│                     ┌────────▼────────┐        │
│                     │ Pinecone + Gemini│       │
│                     └─────────────────┘        │
└─────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
krishi-mitra/
├── backend/
│   ├── core/
│   │   ├── config.py          # RAG configuration
│   │   ├── logging.py         # Structured logging
│   │   └── security.py        # Auth security
│   ├── services/
│   │   ├── embeddings.py      # EmbedNode service
│   │   ├── retrieval.py       # RetrieveNode service
│   │   ├── generation.py      # GenerateNode service
│   │   └── langgraph_pipeline.py  # LangGraph orchestration
│   ├── routers/
│   │   ├── auth.py            # Authentication endpoints
│   │   └── rag.py             # RAG endpoints
│   ├── schemas/
│   │   └── rag.py             # RAG Pydantic models
│   ├── models/
│   │   └── user.py            # User models
│   ├── main.py                # FastAPI application
│   ├── db.py                  # MongoDB connection
│   └── requirements.txt       # Dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- MongoDB
- Pinecone account with existing index
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   cd krishi-mitra/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/rag/health

## 📡 API Endpoints

### Authentication Endpoints

#### `POST /auth/signup`
Register a new farmer with farm details.

**Request:**
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
  "primary_crops": ["rice", "cotton"]
}
```

#### `POST /auth/login`
Login and receive JWT token.

**Request:**
```json
{
  "email": "farmer@example.com",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### `GET /auth/user/me`
Get current user information (requires authentication).

### RAG Endpoints

#### `POST /api/v1/rag/query`
Main RAG endpoint for agricultural questions.

**Request:**
```json
{
  "query": "What is the best fertilizer for rice cultivation in kharif season?",
  "top_k": 5,
  "filters": {"region": "Tamil Nadu"}
}
```

**Response:**
```json
{
  "answer": "For rice cultivation in kharif season, NPK fertilizer with ratio 4:2:1 is recommended...",
  "sources": [
    {
      "source": "rice_cultivation_guide.pdf",
      "page": 15,
      "chunk_id": "chunk_123",
      "score": 0.89
    }
  ],
  "retrieved_chunks": ["text snippet 1", "text snippet 2"],
  "latency_ms": 2432,
  "node_latencies": {
    "embed_ms": 145,
    "retrieve_ms": 387,
    "generate_ms": 1900
  }
}
```

#### `GET /api/v1/rag/health`
Health check for RAG services.

**Response:**
```json
{
  "status": "ok",
  "pinecone": "connected",
  "langgraph": "running",
  "timestamp": "2024-01-15T10:30:00Z",
  "details": {
    "retrieval": {"status": "connected", "total_vectors": 10000},
    "pipeline": {"status": "running"},
    "generation": {"status": "running", "provider": "gemini"}
  }
}
```

#### `POST /api/v1/rag/embed`
Generate embeddings for text (testing/debugging).

#### `GET /api/v1/rag/graph/visualize`
Get LangGraph workflow structure.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017/

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=krishimitra-knowledge

# Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# RAG Settings
DEFAULT_TOP_K=5
MAX_TOP_K=20
MAX_TOKENS=1000
TEMPERATURE=0.7
```

## 🧠 LangGraph RAG Pipeline

The RAG system uses a three-stage LangGraph pipeline:

### Pipeline Flow

```
START → EmbedNode → RetrieveNode → GenerateNode → END
```

1. **EmbedNode**: Converts user query to 768-dim vector using SentenceTransformers
2. **RetrieveNode**: Searches Pinecone for top-k similar document chunks
3. **GenerateNode**: Generates contextual answer using Gemini LLM

### State Management

```python
class RAGState(TypedDict):
    query: str                              # User query
    top_k: int                              # Number of chunks
    filters: Optional[Dict]                 # Metadata filters
    query_embedding: Optional[List[float]]  # From EmbedNode
    retrieved_chunks: Optional[List[Dict]]  # From RetrieveNode
    answer: Optional[str]                   # From GenerateNode
    # Latency tracking for each node
    embed_latency_ms: Optional[float]
    retrieve_latency_ms: Optional[float]
    generate_latency_ms: Optional[float]
```

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Style

The project follows:
- PEP 8 style guide
- Type hints throughout
- Comprehensive docstrings
- Structured logging

## 📊 Performance

**Target Latencies:**
- Embedding: < 200ms
- Retrieval: < 500ms
- Generation: < 3s
- **Total: < 5s end-to-end**

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- API key management via environment variables
- CORS configuration for frontend
- Input validation with Pydantic

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Set strong `SECRET_KEY` in production
- [ ] Configure production MongoDB URL
- [ ] Set up Pinecone production index
- [ ] Configure CORS for production domains
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📄 License

MIT License

## 🆘 Troubleshooting

### Common Issues

**1. MongoDB Connection Error**
- Verify MongoDB is running: `mongod --version`
- Check `MONGO_URL` in `.env`

**2. Pinecone Connection Error**
- Verify API key is correct
- Check index name exists in Pinecone dashboard
- Ensure network connectivity

**3. Embedding Model Loading**
- First run downloads model (~400MB)
- Ensure sufficient disk space
- Check internet connection

**4. Gemini API Errors**
- Verify API key is valid
- Check API quotas in Google Cloud Console
- Ensure model name is correct

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review logs for error details
- Open an issue with detailed information

---

**Built with ❤️ for Indian Farmers**