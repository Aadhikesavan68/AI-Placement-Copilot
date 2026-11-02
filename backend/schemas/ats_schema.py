from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from schemas.roadmap_schema import RoadmapWeek
from schemas.job_schema import JDExtractedData

class ATSCompareRequest(BaseModel):
    resume_id: str
    jd_id: Optional[str] = None
    job_description: Optional[str] = None

class ResumeExtractedData(BaseModel):
    model_config = ConfigDict(extra="ignore")
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
    projects: List[str] = []
    experience: List[str] = []
    internships: List[str] = []
    education: List[str] = []
    certifications: List[str] = []
    achievements: List[str] = []
    languages: List[str] = []
    technologies: List[str] = []
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None

class ATSSubScores(BaseModel):
    skill_match: int = 0
    experience_match: int = 0
    education_match: int = 0
    keyword_match: int = 0
    responsibilities_match: int = 0
    project_relevance: int = 0
    semantic_match: int = 0

class ATSDetails(BaseModel):
    formatting: int = 100
    section_presence: int = 80
    keyword_optimization: int = 75
    readability: int = 85
    contact_information: int = 90
    projects: int = 80
    experience: int = 75
    education: int = 85
    achievements: int = 70
    skills: int = 80
    action_verbs: int = 75
    resume_length: int = 90
    consistency: int = 85

class ATSKeywords(BaseModel):
    existing_keywords: List[str] = []
    missing_keywords: List[str] = []
    recommended_keywords: List[str] = []

class ATSSectionHighlights(BaseModel):
    good_sections: List[str] = []
    weak_sections: List[str] = []
    missing_sections: List[str] = []

class CategorizedMissingSkill(BaseModel):
    skill: str
    category: str = "Critical"  # Critical, Important, Optional
    difficulty: str = "Intermediate"  # Beginner, Intermediate, Advanced
    estimated_hours: str = "15-20 hours"
    priority: str = "High"  # High, Medium, Low
    resource_name: str = "Documentation & Practice Guide"
    resource_url: str = "https://roadmap.sh"

class InterviewQuestion(BaseModel):
    question: str
    category: str = "Technical"
    tip: str = ""

class ATSAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    resume_id: str
    jd_id: Optional[str] = None
    resume_name: Optional[str] = None
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    ats_score: int
    match_score: int
    interview_readiness: int = 70
    company_readiness: int = 70
    confidence_score: int = 90
    semantic_match: int = 75
    scores: ATSSubScores
    ats_details: ATSDetails
    resume_data: ResumeExtractedData
    jd_data: JDExtractedData
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    extra_skills: List[str] = []
    missing_skills_categorized: List[CategorizedMissingSkill] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    keywords: ATSKeywords
    ai_suggestions: List[str] = []
    highlights: ATSSectionHighlights
    interview_questions: List[InterviewQuestion] = []
    roadmap: List[RoadmapWeek] = []
    created_at: datetime

class AnalysisHistoryItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    resume_id: str
    resume_name: str = "Candidate Resume"
    company_name: str = "Target Company"
    role: str = "Software Engineer"
    match_score: int = 0
    ats_score: int = 0
    interview_readiness: int = 0
    missing_skills_count: int = 0
    created_at: datetime
