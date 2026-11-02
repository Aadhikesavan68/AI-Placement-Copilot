from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CandidateSkill(BaseModel):
    skill: str
    category: str
    sources: List[str] = Field(default_factory=list)
    occurrences: int = 1
    current_level: Optional[str] = None
    latest_score: Optional[int] = None
    last_assessed: Optional[datetime] = None


class SkillSelection(BaseModel):
    skills: List[str] = Field(min_length=1)


class AssessmentStart(BaseModel):
    skill: str = Field(min_length=1, max_length=80)
    self_reported_level: Literal["Beginner", "Intermediate", "Advanced"] = "Beginner"
    reassessment: bool = False


class AssessmentAnswer(BaseModel):
    question_id: str
    answer: int = Field(ge=0)


class AssessmentQuestion(BaseModel):
    id: str
    skill: str
    category: str
    topic: str
    difficulty: str
    question: str
    options: List[str]
    sequence: int


class GeneratedQuestion(BaseModel):
    id: str
    category: str
    topic: str
    difficulty: str
    question: str
    options: List[str] = Field(min_length=2)
    answer: int = Field(ge=0, le=5)


class AssessmentStartResponse(BaseModel):
    assessment_id: str
    skill: str
    total_questions: int
    question: AssessmentQuestion


class AssessmentResult(BaseModel):
    id: str
    skill: str
    score: int
    level: str
    total_questions: int
    correct_answers: int
    difficulty_reached: str
    topic_scores: dict
    weak_topics: List[str]
    strong_topics: List[str]
    time_taken_seconds: int
    created_at: datetime


class SkillProfile(BaseModel):
    skills: List[CandidateSkill]


class SkillPriority(BaseModel):
    skill: str
    level: Optional[str] = None
    score: Optional[int] = None
    required_by_jd: bool
    priority: str
    weak_topics: List[str] = Field(default_factory=list)


class SkillPriorityResponse(BaseModel):
    skills: List[SkillPriority]
