from typing import TypedDict, List, Any

class CourseRecommendationDict(TypedDict):
    course_name: str
    provider: str
    difficulty: str
    estimated_duration: str
    url: str

class RoadmapWeekDict(TypedDict):
    week: int
    topic: str
    description: str
    resources: List[CourseRecommendationDict]

class RoadmapDBModel(TypedDict):
    _id: Any
    analysis_id: str
    weeks: List[RoadmapWeekDict]
