def analyze_strengths(matched_skills: list, resume_projects: list, resume_experience: list) -> dict:
    return {
        "strong_skills": matched_skills,
        "relevant_experience": len(resume_experience) > 0,
        "project_count": len(resume_projects),
        "matching_technologies": matched_skills
    }

def analyze_weaknesses(missing_skills: list) -> dict:
    categories = {
        "frameworks": ["React", "Angular", "Vue.js", "Spring Boot", "Django", "Flask", "Node.js"],
        "databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "NoSQL", "DynamoDB"],
        "cloud": ["AWS", "GCP", "Azure"],
        "core": ["Data Structures", "Algorithms", "System Design"]
    }
    
    missing_frameworks = [s for s in missing_skills if s in categories["frameworks"]]
    missing_databases = [s for s in missing_skills if s in categories["databases"]]
    missing_cloud = [s for s in missing_skills if s in categories["cloud"]]
    missing_core = [s for s in missing_skills if s in categories["core"]]
    
    return {
        "missing_skills": missing_skills,
        "missing_frameworks": missing_frameworks,
        "missing_databases": missing_databases,
        "missing_cloud": missing_cloud,
        "weak_topics": missing_core
    }
