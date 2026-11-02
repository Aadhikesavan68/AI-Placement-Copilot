from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class CompanyBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    company_name: str
    company_logo: Optional[str] = None
    description: Optional[str] = None
    total_questions: int = 0
    topics: List[str] = []

class CompanyCreate(CompanyBase):
    pass

class CompanyInDB(CompanyBase):
    id: str
    created_at: Optional[datetime] = None

class CompanyResponse(CompanyInDB):
    pass

class CompanyStatsResponse(BaseModel):
    total_questions: int
    easy: int
    medium: int
    hard: int

class CompanyTopicResponse(BaseModel):
    topic: str
    count: int

class BookmarkResponse(BaseModel):
    success: bool
    bookmarked: bool
