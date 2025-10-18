from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, rag

app = FastAPI(
    title="Krishi Mitra Backend",
    description="Backend API for Krishi Mitra agricultural application with AI-powered RAG system",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["rag"])

@app.get("/")
def root():
    return {
        "message": "Krishi Mitra Backend Running",
        "version": "2.0.0",
        "features": ["Authentication", "RAG AI Assistant"],
        "docs": "/docs"
    }
