# 🚀 Krishi Mitra Setup Guide

Complete step-by-step guide to set up the Krishi Mitra backend with RAG system.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] MongoDB installed and running
- [ ] Pinecone account created
- [ ] Google Cloud account with Gemini API access
- [ ] Git installed

## 🔧 Step-by-Step Setup

### Step 1: Environment Setup

```bash
# Navigate to backend directory
cd krishi-mitra/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.9+
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - FastAPI and Uvicorn (web framework)
# - LangGraph and LangChain (RAG orchestration)
# - Pinecone (vector database)
# - SentenceTransformers (embeddings)
# - Google Generative AI (Gemini)
# - MongoDB driver
# - Authentication libraries
```

**Note**: First-time installation may take 5-10 minutes as it downloads the embedding model (~400MB).

### Step 3: MongoDB Setup

```bash
# Start MongoDB (if not running)
# On macOS:
brew services start mongodb-community

# On Linux:
sudo systemctl start mongod

# On Windows:
net start MongoDB

# Verify MongoDB is running
mongosh --eval "db.version()"
```

### Step 4: Pinecone Setup

1. **Create Pinecone Account**
   - Go to https://www.pinecone.io/
   - Sign up for free account
   - Create a new project

2. **Create Index**
   ```python
   # You can create index via Pinecone console or using this script:
   from pinecone import Pinecone, ServerlessSpec
   
   pc = Pinecone(api_key="your-api-key")
   
   pc.create_index(
       name="krishimitra-knowledge",
       dimension=768,  # Must match embedding model dimension
       metric="cosine",
       spec=ServerlessSpec(
           cloud="aws",
           region="us-east-1"
       )
   )
   ```

3. **Get API Key**
   - Go to Pinecone Console → API Keys
   - Copy your API key

### Step 5: Gemini API Setup

1. **Get Gemini API Key**
   - Go to https://makersuite.google.com/app/apikey
   - Create new API key
   - Copy the key

2. **Test API Key** (optional)
   ```python
   import google.generativeai as genai
   
   genai.configure(api_key="your-api-key")
   model = genai.GenerativeModel('gemini-2.0-flash-exp')
   response = model.generate_content("Hello")
   print(response.text)
   ```

### Step 6: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Required Configuration:**

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017/

# JWT (Generate a secure random key)
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Pinecone
PINECONE_API_KEY=pcsk_xxxxx  # Your Pinecone API key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=krishimitra-knowledge

# Gemini
GEMINI_API_KEY=AIzaSyxxxxx  # Your Gemini API key
GEMINI_MODEL=gemini-2.0-flash-exp

# RAG Settings (optional, defaults provided)
DEFAULT_TOP_K=5
MAX_TOP_K=20
MAX_TOKENS=1000
TEMPERATURE=0.7
```

**Generate Secure SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Step 7: Verify Installation

```bash
# Check if all imports work
python -c "
from services.langgraph_pipeline import rag_pipeline
from services.embeddings import embedding_service
from services.retrieval import retrieval_service
from services.generation import generation_service
print('✅ All imports successful!')
"
```

### Step 8: Start the Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Loading embedding model: sentence-transformers/all-mpnet-base-v2
INFO:     Embedding model loaded successfully. Dimension: 768
INFO:     Successfully connected to Pinecone index: krishimitra-knowledge
INFO:     Initialized Gemini model: gemini-2.0-flash-exp
INFO:     LangGraph RAG Pipeline initialized
✅ MongoDB connected successfully!
```

### Step 9: Test the API

**1. Check Root Endpoint:**
```bash
curl http://localhost:8000/
```

**2. Check API Documentation:**
Open browser: http://localhost:8000/docs

**3. Test Health Check:**
```bash
curl http://localhost:8000/api/v1/rag/health
```

**4. Test Authentication:**
```bash
# Signup
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test Farmer",
    "phone_number": "9876543210",
    "state": "Tamil Nadu",
    "district": "Coimbatore",
    "village": "Test Village",
    "pincode": "642001",
    "farm_size": "medium",
    "primary_crops": ["rice", "wheat"]
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**5. Test RAG Query:**
```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the best fertilizer for rice?",
    "top_k": 5
  }'
```

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Solution:**
```bash
pip install sentence-transformers
```

### Issue: "MongoDB connection failed"

**Solution:**
```bash
# Check if MongoDB is running
mongosh

# If not running, start it
brew services start mongodb-community  # macOS
sudo systemctl start mongod  # Linux
```

### Issue: "Pinecone index not found"

**Solution:**
1. Verify index name in Pinecone console
2. Check if index is in correct environment
3. Ensure index dimension is 768

### Issue: "Gemini API quota exceeded"

**Solution:**
1. Check quota in Google Cloud Console
2. Wait for quota reset
3. Consider upgrading plan

### Issue: "Embedding model download fails"

**Solution:**
```bash
# Download manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-mpnet-base-v2')"
```

## 📊 Performance Optimization

### For Development
- Use `--reload` flag for auto-reload
- Set `LOG_LEVEL=DEBUG` for detailed logs
- Use smaller `top_k` values (3-5)

### For Production
- Use multiple workers: `--workers 4`
- Set `LOG_LEVEL=WARNING`
- Enable caching for frequent queries
- Use production-grade MongoDB cluster
- Consider GPU for faster embeddings

## 🔐 Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Use strong passwords
- [ ] Enable HTTPS in production
- [ ] Restrict CORS origins
- [ ] Keep API keys in `.env` (never commit)
- [ ] Regular security updates
- [ ] Enable MongoDB authentication
- [ ] Use environment-specific configs

## 📝 Next Steps

After successful setup:

1. **Populate Pinecone Index**
   - Upload your agricultural documents
   - Generate embeddings
   - Store in Pinecone

2. **Customize RAG Prompt**
   - Edit `services/generation.py`
   - Modify `_create_rag_prompt()` method

3. **Add Frontend**
   - Connect React/Vue frontend
   - Use JWT tokens for auth
   - Call RAG endpoints

4. **Deploy to Production**
   - Use Docker for containerization
   - Deploy to cloud (AWS, GCP, Azure)
   - Set up CI/CD pipeline

## 🆘 Getting Help

- **Documentation**: Check `/docs` endpoint
- **Logs**: Check console output for errors
- **Health Check**: Use `/api/v1/rag/health`
- **Issues**: Open GitHub issue with logs

---

**Setup Complete! 🎉**

Your Krishi Mitra backend is now ready to serve agricultural queries with AI-powered responses.
