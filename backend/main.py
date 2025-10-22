from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, rag, weather, crop_predict, fertilizer_predict

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
app.include_router(weather.router, prefix="/weather", tags=["weather"])
app.include_router(crop_predict.router, prefix="/crop_predict", tags=["crop_predict"])
app.include_router(fertilizer_predict.router, prefix="/fertilizer_predict", tags=["fertilizer_predict"])

@app.get("/")
def root():
    return {
        "message": "Krishi Mitra Backend Running",
        "version": "2.0.0",
        "features": ["Authentication", "RAG AI Assistant", "Crop Prediction", "Fertilizer Prediction"],
        "docs": "/docs"
    }
