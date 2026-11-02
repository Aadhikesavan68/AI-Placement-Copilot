from pydantic import BaseModel
from typing import List, Optional

class QuestionBase(BaseModel):
    company: str
    title: str
    difficulty: str
    topic: str
    leetcode_link: Optional[str] = None
    tags: List[str] = []

class QuestionCreate(QuestionBase):
    pass

class QuestionInDB(QuestionBase):
    id: str
    completed: bool = False
    bookmarked: bool = False

class QuestionResponse(QuestionInDB):
    pass

class CompanyQuestionsResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int
