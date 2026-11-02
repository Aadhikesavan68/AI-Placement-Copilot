from repositories.resume_repository import get_resume_by_id
from utils.company_skill_loader import get_company_profile
from services.skill_gap_service import analyze_strengths, analyze_weaknesses
from services.roadmap_service import generate_roadmap
from services.jd_service import parse_job_description
from utils.skill_extractor import normalize_skills
from bson import ObjectId

async def run_analysis(user_id: str, resume_id: str, company_name: str = None, jd_text: str = None) -> dict:
    # 1. Fetch Resume
    resume = await get_resume_by_id(resume_id, user_id)
    if not resume:
        raise ValueError("Resume not found")
        
    resume_skills = normalize_skills(resume.get("skills", []))
    resume_projects = resume.get("projects", [])
    resume_experience = resume.get("experience", [])
    
    # 2. Get Target Profile (Company or JD)
    if company_name:
        target_profile = await get_company_profile(company_name)
        if not target_profile:
            raise ValueError(f"Company profile for {company_name} not found")
    elif jd_text:
        target_profile = parse_job_description(jd_text)
    else:
        raise ValueError("Must provide either company_name or jd_text")
        
    required_skills = target_profile.get("skills", [])
    preferred_skills = target_profile.get("preferred_skills", [])
    important_topics = target_profile.get("important_topics", [])
    
    # 3. Calculate Match
    matched_skills = [s for s in resume_skills if s in required_skills]
    missing_skills = [s for s in required_skills if s not in resume_skills]
    extra_skills = [s for s in resume_skills if s not in required_skills]
    
    # Simple Match Percentage Formula
    if len(required_skills) == 0:
        match_percentage = 100.0 if len(matched_skills) > 0 else 0.0
    else:
        # Base match from required
        base_match = (len(matched_skills) / len(required_skills)) * 80 
        # Bonus match from preferred
        matched_preferred = [s for s in resume_skills if s in preferred_skills]
        bonus = min(20, len(matched_preferred) * 5) # 5 points per preferred skill, max 20
        match_percentage = round(min(100.0, base_match + bonus), 1)
        
    # 4. Strengths & Weaknesses
    strengths = analyze_strengths(matched_skills, resume_projects, resume_experience)
    weaknesses = analyze_weaknesses(missing_skills)
    
    # 5. Roadmap
    roadmap = generate_roadmap(None, missing_skills, important_topics)
    
    # 6. Recommendations
    recommendations = {
        "resume_improvements": [],
        "interview_focus": important_topics
    }
    
    if len(resume_projects) < 2:
        recommendations["resume_improvements"].append("Add more technical projects to demonstrate your skills.")
    if len(resume_experience) == 0:
        recommendations["resume_improvements"].append("Highlight internships, open-source contributions, or freelance work.")
        
    return {
        "user_id": user_id,
        "resume_id": resume_id,
        "company_name": company_name,
        "job_description": jd_text,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "match_percentage": match_percentage,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "roadmap": [w.model_dump() for w in roadmap],
        "recommendations": recommendations
    }
