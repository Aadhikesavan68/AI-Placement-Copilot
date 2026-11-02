from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class JDExtractedData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    company_name: Optional[str] = "Target Company"
    job_title: Optional[str] = None
    role: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    responsibilities: List[str] = []
    experience: Optional[str] = None
    required_experience: Optional[str] = None
    education: List[str] = []
    keywords: List[str] = []
    technologies: List[str] = []
    tools: List[str] = []
    soft_skills: List[str] = []

class JobDescriptionBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    jd_name: str
    jd_text: str
    original_file: Optional[str] = None
    extracted_data: Optional[JDExtractedData] = None

class JobDescriptionCreate(JobDescriptionBase):
    user_id: str

class JobDescriptionInDB(JobDescriptionCreate):
    id: str
    upload_date: datetime

class JobDescriptionResponse(JobDescriptionInDB):
    pass

class JobUploadTextRequest(BaseModel):
    title: Optional[str] = None
    text: str

class DeleteJobResponse(BaseModel):
    success: bool
    message: str
