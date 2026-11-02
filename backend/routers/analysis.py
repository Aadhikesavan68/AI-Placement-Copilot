from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import os
from schemas.user_schema import User
from routers.auth import get_current_user
from schemas.analysis_schema import AnalysisRequestCompany, AnalysisRequestJD, AnalysisResponse
from schemas.ats_schema import ATSCompareRequest, ATSAnalysisResponse
from services.analysis_service import run_analysis
from services.ai_service import run_ai_analysis
from repositories.analysis_repository import (
    save_ats_analysis, get_user_ats_analyses, get_ats_analysis_by_id,
    delete_ats_analysis_by_id, get_job_description_by_id
)
from repositories.resume_repository import get_resume_by_id

router = APIRouter()

@router.post("/compare", response_model=ATSAnalysisResponse)
async def compare_resume_and_job(req: ATSCompareRequest, current_user: User = Depends(get_current_user)):
    """
    Core AI & Deterministic ATS Comparison Engine.
    Evaluates Resume vs Job Description across 12 ATS metrics, skill competencies, 
    action verbs, project relevance, and produces categorized missing skills + 4-week roadmap.
    """
    # 1. Fetch Resume
    resume = await get_resume_by_id(req.resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # 2. Get JD Text
    jd_text = ""
    jd_id = req.jd_id
    jd_doc = None
    if jd_id:
        jd_doc = await get_job_description_by_id(jd_id, current_user.id)
        if not jd_doc:
            raise HTTPException(status_code=404, detail="Job Description not found")
        jd_text = jd_doc.get("jd_text", "")
    elif req.job_description:
        jd_text = req.job_description
    else:
        raise HTTPException(status_code=400, detail="Must provide either jd_id or job_description text")
        
    # 3. Run Comparison
    try:
        file_ext = os.path.splitext(resume.get("original_file", "resume.pdf"))[1].lower().replace(".", "")
        analysis_data, jd_data = await run_ai_analysis(resume, jd_text, file_ext)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e}")
        
    # 4. Save and return
    resume_name = resume.get("resume_name") or "Candidate Resume"
    company_name = jd_data.get("company_name") or "Target Company"
    role_title = jd_data.get("role") or jd_data.get("job_title") or "Software Engineer"
    
    full_analysis = {
        "user_id": current_user.id,
        "resume_id": req.resume_id,
        "jd_id": jd_id,
        "resume_name": resume_name,
        "company_name": company_name,
        "role_title": role_title,
        "ats_score": analysis_data.get("ats_score", 75),
        "match_score": analysis_data.get("match_score", 80),
        "interview_readiness": analysis_data.get("interview_readiness", 75),
        "company_readiness": analysis_data.get("company_readiness", 70),
        "confidence_score": analysis_data.get("confidence_score", 90),
        "semantic_match": analysis_data.get("semantic_match", 75),
        "scores": analysis_data.get("scores", {}),
        "ats_details": analysis_data.get("ats_details", {}),
        "resume_data": {
            "name": resume.get("name") or "Candidate",
            "email": resume.get("email"),
            "phone": resume.get("phone"),
            "college": resume.get("college"),
            "degree": resume.get("degree"),
            "skills": resume.get("skills", []),
            "languages_prog": resume.get("languages_prog", []),
            "frameworks": resume.get("frameworks", []),
            "databases": resume.get("databases", []),
            "cloud": resume.get("cloud", []),
            "tools": resume.get("tools", []),
            "soft_skills": resume.get("soft_skills", []),
            "projects": resume.get("projects", []),
            "experience": resume.get("experience", []),
            "internships": resume.get("internships", []),
            "education": resume.get("education", []),
            "certifications": resume.get("certifications", []),
            "achievements": resume.get("achievements", []),
            "languages": resume.get("languages", []),
            "technologies": resume.get("technologies", []),
            "linkedin": resume.get("linkedin"),
            "github": resume.get("github"),
            "portfolio": resume.get("portfolio")
        },
        "jd_data": jd_data,
        "matched_skills": analysis_data.get("matched_skills", []),
        "missing_skills": analysis_data.get("missing_skills", []),
        "extra_skills": analysis_data.get("extra_skills", []),
        "missing_skills_categorized": analysis_data.get("missing_skills_categorized", []),
        "strengths": analysis_data.get("strengths", []),
        "weaknesses": analysis_data.get("weaknesses", []),
        "suggestions": analysis_data.get("suggestions", []),
        "keywords": analysis_data.get("keywords", {}),
        "ai_suggestions": analysis_data.get("ai_suggestions", []),
        "highlights": analysis_data.get("highlights", {}),
        "interview_questions": analysis_data.get("interview_questions", []),
        "roadmap": analysis_data.get("roadmap", [])
    }
    
    saved = await save_ats_analysis(full_analysis)
    return saved

@router.get("/history", response_model=List[ATSAnalysisResponse])
async def get_history(
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("date_desc"),
    current_user: User = Depends(get_current_user)
):
    """Fetches user ATS comparison history with search & sorting."""
    return await get_user_ats_analyses(current_user.id, search or "", sort_by or "date_desc")

@router.get("/history/{id}", response_model=ATSAnalysisResponse)
async def get_history_by_id(id: str, current_user: User = Depends(get_current_user)):
    analysis = await get_ats_analysis_by_id(id, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.get("/{id}", response_model=ATSAnalysisResponse)
async def get_ats_analysis(id: str, current_user: User = Depends(get_current_user)):
    analysis = await get_ats_analysis_by_id(id, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="ATS Analysis not found")
    return analysis

@router.delete("/{id}")
async def delete_analysis(id: str, current_user: User = Depends(get_current_user)):
    """Deletes an ATS analysis from history."""
    deleted = await delete_ats_analysis_by_id(id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found or could not be deleted")
    return {"success": True, "message": "Analysis deleted successfully"}

# Legacy company & custom JD endpoints
@router.post("/company", response_model=AnalysisResponse)
async def analyze_company(req: AnalysisRequestCompany, current_user: User = Depends(get_current_user)):
    try:
        analysis_data = await run_analysis(
            user_id=current_user.id,
            resume_id=req.resume_id,
            company_name=req.company_name
        )
        return await save_ats_analysis(analysis_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/jd", response_model=AnalysisResponse)
async def analyze_jd(req: AnalysisRequestJD, current_user: User = Depends(get_current_user)):
    try:
        analysis_data = await run_analysis(
            user_id=current_user.id,
            resume_id=req.resume_id,
            jd_text=req.job_description
        )
        return await save_ats_analysis(analysis_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
