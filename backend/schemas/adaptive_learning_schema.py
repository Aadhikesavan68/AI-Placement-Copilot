from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class LearningPlanCreate(BaseModel):
    analysis_id: str
    daily_minutes: int = Field(ge=15, le=720)
    learning_days: List[int] = Field(min_length=1, max_length=7)
    start_date: date
    target_date: date
    missing_skills: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_plan(self):
        if any(day < 0 or day > 6 for day in self.learning_days):
            raise ValueError("learning_days must use weekday values from 0 to 6")
        if self.target_date < self.start_date:
            raise ValueError("target_date must be on or after start_date")
        return self


class TaskUpdate(BaseModel):
    status: str = Field(pattern="^(planned|started|completed|skipped)$")
    actual_minutes: Optional[int] = Field(default=None, ge=0, le=1440)


class LearningSessionCreate(BaseModel):
    task_id: str
    minutes: int = Field(gt=0, le=1440)


class MockTestSubmit(BaseModel):
    answers: List[int]


class LearningPlanResponse(BaseModel):
    id: str
    analysis_id: str
    daily_minutes: int
    learning_days: List[int]
    start_date: date
    target_date: date
    total_sessions: int
    total_planned_minutes: int
    completed_minutes: int
    progress_percent: float
    streak_days: int
    skills: List[dict]
    tasks: List[dict]
    mock_tests: List[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class MockQuestion(BaseModel):
    question: str
    options: List[str]


class MockTestResponse(BaseModel):
    id: str
    skill: str
    questions: List[MockQuestion]
    status: str
    score: Optional[int] = None
    weak_topics: List[str] = Field(default_factory=list)


class MockTestResult(BaseModel):
    id: str
    skill: str
    score: int
    total: int
    weak_topics: List[str]
    submitted_at: datetime
