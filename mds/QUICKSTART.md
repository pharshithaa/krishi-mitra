# ⚡ Krishi Mitra - 5 Minute Quickstart

Get your Krishi Mitra RAG backend up and running in 5 minutes!

## 🎯 What You'll Need

- Python 3.9+
- MongoDB running locally
- Pinecone API key ([Get it here](https://www.pinecone.io/))
- Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

## 🚀 Quick Setup

### 1. Install Dependencies (2 minutes)

```bash
cd krishi-mitra/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your keys
nano .env
```

**Minimum required configuration:**
```env
MONGO_URL=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-change-this
PINECONE_API_KEY=your_pinecone_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### 3. Start Server (30 seconds)

```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Loading embedding model...
INFO:     Embedding model loaded successfully
INFO:     Successfully connected to Pinecone
INFO:     LangGraph RAG Pipeline initialized
✅ MongoDB connected successfully!
```

### 4. Test It! (1 minute)

Open http://localhost:8000/docs in your browser.

Or test with curl:

```bash
# Health check
curl http://localhost:8000/api/v1/rag/health

# Test query
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the best fertilizer for rice?", "top_k": 3}'
```

## ✅ You're Done!

Your RAG backend is now running at http://localhost:8000

**Next Steps:**
- 📖 Read [README.md](README.md) for full documentation
- 🔧 Check [SETUP.md](backend/SETUP.md) for detailed setup
- 📡 See [API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md) for API reference
- 🚀 Review [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## 🆘 Quick Troubleshooting

**Server won't start?**
- Check MongoDB is running: `mongosh`
- Verify Python version: `python --version` (should be 3.9+)

**Pinecone errors?**
- Verify API key is correct
- Check index name exists in Pinecone dashboard

**Gemini errors?**
- Verify API key is valid
- Check you have API quota available

**Need help?** Check the full [SETUP.md](backend/SETUP.md) guide.

---

**Happy Coding! 🌾**
