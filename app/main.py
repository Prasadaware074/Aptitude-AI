import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config.settings import settings
from app.database.init_db import seed_database
from app.api.routes import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Aptitude Preparation System API",
    description="Production-quality Aptitude AI preparation engine powered by Google Gemini, LangChain, and LangGraph.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount Frontend static files
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.on_event("startup")
def startup_event():
    logger.info("Initializing Aptitude AI System database and vector index...")
    seed_database()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "system": "Multi-Agent Aptitude Preparation System",
        "model": settings.MODEL_NAME,
        "gemini_api_configured": bool(settings.GOOGLE_API_KEY)
    }

@app.get("/")
def serve_frontend_root():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Multi-Agent Aptitude Preparation System API is running. Access /docs for API documentation."}
