from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from schemas.roadmap_schema import RoadmapWeek

class AnalysisRequestCompany(BaseModel):
    resume_id: str
    company_name: str

class AnalysisRequestJD(BaseModel):
    resume_id: str
    job_description: str

class AnalysisBase(BaseModel):
    user_id: str
    resume_id: str
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    resume_skills: List[str] = []
    required_skills: List[str] = []
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    extra_skills: List[str] = []
    match_percentage: float = 0.0
    strengths: Dict[str, Any] = {}
    weaknesses: Dict[str, Any] = {}
    recommendations: Dict[str, Any] = {}
    roadmap: List[RoadmapWeek] = []
    
class AnalysisInDB(AnalysisBase):
    id: str
    created_at: datetime

class AnalysisResponse(AnalysisInDB):
    pass
