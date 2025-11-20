# main.py - FastAPI application entry point
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db
from routers import documents, analyses, dashboard

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Legal Risk Analysis API",
    description="API for analyzing legal documents and identifying risks",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads and outputs
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
outputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")

os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(outputs_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(analyses.router, prefix="/api/analyses", tags=["Analyses"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Legal Risk Analysis API",
        "docs": "/api/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
