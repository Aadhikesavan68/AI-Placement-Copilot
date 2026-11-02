from pydantic import BaseModel
from typing import List, Optional

class CourseRecommendation(BaseModel):
    course_name: str
    provider: str
    difficulty: str
    estimated_duration: str
    url: str

class RoadmapWeek(BaseModel):
    week: int
    topic: str
    description: str
    resources: List[CourseRecommendation]

class RoadmapBase(BaseModel):
    analysis_id: str
    weeks: List[RoadmapWeek]

class RoadmapInDB(RoadmapBase):
    id: str

class RoadmapResponse(RoadmapInDB):
    pass
