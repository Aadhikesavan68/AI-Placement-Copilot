import uuid
from schemas.roadmap_schema import RoadmapWeek, CourseRecommendation

# Static resource mapping for missing skills
RESOURCES = {
    "React": CourseRecommendation(course_name="React - The Complete Guide", provider="Udemy", difficulty="Beginner", estimated_duration="40h", url="https://www.udemy.com/course/react-the-complete-guide-incl-redux/"),
    "Data Structures": CourseRecommendation(course_name="Data Structures and Algorithms", provider="Coursera", difficulty="Intermediate", estimated_duration="20h", url="https://www.coursera.org/specializations/data-structures-algorithms"),
    "System Design": CourseRecommendation(course_name="Grokking the System Design Interview", provider="Educative", difficulty="Advanced", estimated_duration="15h", url="https://www.educative.io/courses/grokking-the-system-design-interview"),
    "AWS": CourseRecommendation(course_name="AWS Certified Solutions Architect", provider="AWS Skill Builder", difficulty="Intermediate", estimated_duration="25h", url="https://skillbuilder.aws/"),
    "Python": CourseRecommendation(course_name="100 Days of Code: Python", provider="Udemy", difficulty="Beginner", estimated_duration="60h", url="https://www.udemy.com/course/100-days-of-code/"),
    "Java": CourseRecommendation(course_name="Java Programming Masterclass", provider="Udemy", difficulty="Beginner", estimated_duration="80h", url="https://www.udemy.com/course/java-the-complete-java-developer-course/")
}

def get_default_course(skill: str) -> CourseRecommendation:
    return CourseRecommendation(
        course_name=f"Mastering {skill}",
        provider="YouTube / freeCodeCamp",
        difficulty="Intermediate",
        estimated_duration="10h",
        url=f"https://www.youtube.com/results?search_query={skill}+tutorial"
    )

def generate_roadmap(analysis_id: str, missing_skills: list, important_topics: list) -> list:
    weeks = []
    week_num = 1
    
    # 1. First, address core missing skills
    for skill in missing_skills:
        course = RESOURCES.get(skill) or get_default_course(skill)
        weeks.append(RoadmapWeek(
            week=week_num,
            topic=f"Learn {skill}",
            description=f"Focus on fundamentals and practical application of {skill}.",
            resources=[course]
        ))
        week_num += 1
        
    # 2. Then, address important interview topics if any
    for topic in important_topics[:3]: # limit to top 3
        course = get_default_course(topic)
        weeks.append(RoadmapWeek(
            week=week_num,
            topic=f"Interview Prep: {topic}",
            description=f"Practice common interview problems related to {topic}.",
            resources=[course]
        ))
        week_num += 1
        
    return weeks
