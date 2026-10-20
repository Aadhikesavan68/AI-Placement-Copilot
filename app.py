import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for AI Placement Copilot",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import resume, jobs, skills, interview, company, roadmap

# Include routers
app.include_router(resume.router, prefix=settings.API_V1_STR + "/upload-resume", tags=["Resume"])
app.include_router(jobs.router, prefix=settings.API_V1_STR + "/jobs", tags=["Jobs"])
app.include_router(skills.router, prefix=settings.API_V1_STR + "/skills", tags=["Skills"])
app.include_router(interview.router, prefix=settings.API_V1_STR + "/interview", tags=["Interview"])
app.include_router(company.router, prefix=settings.API_V1_STR + "/company", tags=["Company"])
app.include_router(roadmap.router, prefix=settings.API_V1_STR + "/roadmap", tags=["Roadmap"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    logger.info("Health check endpoint called.")
    return {"status": "ok", "message": "AI Placement Copilot Backend is running."}

if __name__ == "__main__":
    import uvicorn
    # Allow running the app directly via `python app.py` for development
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
