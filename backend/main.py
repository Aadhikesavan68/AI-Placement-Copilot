from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from database.mongo import close_mongo_connection, connect_to_mongo
from routers import adaptive_learning, analysis, auth, company, resume, job, resume_grammar, skill_assessment
from utils.company_skill_loader import seed_company_skills


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await connect_to_mongo()
    try:
        await seed_company_skills()
    except Exception as exc:
        print(f"Warning: could not seed company skills: {exc}")
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(resume.router, prefix=f"{settings.API_V1_STR}/resume", tags=["resume"])
app.include_router(company.router, prefix=f"{settings.API_V1_STR}/company", tags=["company"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis"])
app.include_router(job.router, prefix=f"{settings.API_V1_STR}/job", tags=["job"])
app.include_router(resume_grammar.router, prefix=f"{settings.API_V1_STR}/resume-grammar", tags=["resume-grammar"])
app.include_router(adaptive_learning.router, prefix=f"{settings.API_V1_STR}/learning", tags=["adaptive-learning"])
app.include_router(skill_assessment.router, prefix=f"{settings.API_V1_STR}", tags=["skill-assessment"])


@app.get("/")
def read_root():
    return {"message": "Welcome to AI Placement Copilot API"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
