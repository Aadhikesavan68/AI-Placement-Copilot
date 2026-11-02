from typing import TypedDict, List, Dict, Any
from datetime import datetime

class AnalysisDBModel(TypedDict):
    _id: Any
    user_id: str
    resume_id: str
    company_name: str
    job_description: str
    resume_skills: List[str]
    required_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    match_percentage: float
    strengths: Dict[str, Any]
    weaknesses: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_at: datetime
