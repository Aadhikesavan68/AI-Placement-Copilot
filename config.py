import os
from pathlib import Path
from pydantic import BaseModel

# Base directories
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

class Settings(BaseModel):
    """
    Application settings and configurations.
    """
    # API Configurations
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Placement Copilot"

    # Directories
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DATA_DIR: Path = BASE_DIR / "datasets" / "processed"

    # Dataset Paths
    CLEAN_JOBS_PATH: Path = DATA_DIR / "clean_jobs.csv"
    PROCESSED_RESUMES_PATH: Path = DATA_DIR / "processed_resumes.csv"
    COMPANY_QUESTIONS_PATH: Path = DATA_DIR / "company_questions_clean.csv"
    HR_QUESTIONS_PATH: Path = DATA_DIR / "hr_questions.csv"
    
    # New Mock Dataset Paths
    COMPANY_SKILLS_PATH: Path = DATA_DIR / "company_skills.csv"
    COMPANY_PROFILES_PATH: Path = DATA_DIR / "company_profiles.csv"
    LEARNING_RESOURCES_PATH: Path = DATA_DIR / "learning_resources.csv"
    INTERVIEW_QUESTIONS_PATH: Path = DATA_DIR / "interview_questions.csv"

    # AI Model Settings
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: Path = DATA_DIR / "faiss_index.bin"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
