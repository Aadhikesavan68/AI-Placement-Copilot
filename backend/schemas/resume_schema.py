from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ResumeBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    resume_name: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    skills: List[str] = []
    languages_prog: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    cloud: List[str] = []
    tools: List[str] = []
    soft_skills: List[str] = []
    education: List[str] = []
    projects: List[str] = []
    experience: List[str] = []
    internships: List[str] = []
    certifications: List[str] = []
    achievements: List[str] = []
    languages: List[str] = []
    technologies: List[str] = []
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None

class ResumeCreate(ResumeBase):
    user_id: str
    original_file: str

class ResumeInDB(ResumeCreate):
    id: str
    upload_date: datetime

class ResumeResponse(ResumeInDB):
    completion_score: int

class DeleteResponse(BaseModel):
    success: bool
    message: str
