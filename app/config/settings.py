import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # API & LLM
    GOOGLE_API_KEY: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    MODEL_NAME: str = Field(default_factory=lambda: os.getenv("MODEL_NAME", "gemini-2.5-flash"))
    TEMPERATURE: float = Field(default_factory=lambda: float(os.getenv("TEMPERATURE", "0.2")))
    MAX_RETRIES: int = Field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))

    # Paths
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/aptitude.db"))
    VECTOR_DB_PATH: str = Field(default_factory=lambda: os.getenv("VECTOR_DB_PATH", str(BASE_DIR / "data" / "chroma_db")))
    KNOWLEDGE_BASE_DIR: str = Field(default_factory=lambda: os.getenv("KNOWLEDGE_BASE_DIR", str(BASE_DIR / "knowledge_base")))

    # RAG Settings
    CHUNK_SIZE: int = Field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "500")))
    CHUNK_OVERLAP: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "50")))

    # Thresholds
    MIN_ATTEMPTS_FOR_WEAK_ANALYSIS: int = 2

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure required directories exist
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
