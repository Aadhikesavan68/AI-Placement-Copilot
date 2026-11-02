from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from repositories.resume_repository import get_resume_by_id, get_resumes_by_user
from repositories.skill_assessment_repository import (
    get_candidate_skill,
    get_latest_assessment,
    get_latest_assessments,
    get_session,
    list_assessments,
    list_candidate_skills,
    save_assessment,
    save_session,
    update_candidate_skill,
    update_session,
    upsert_candidate_skills,
)
from routers.auth import get_current_user
from schemas.skill_assessment_schema import (
    AssessmentAnswer,
    AssessmentQuestion,
    AssessmentResult,
    AssessmentStart,
    AssessmentStartResponse,
    CandidateSkill,
    SkillProfile,
    SkillPriorityResponse,
    SkillSelection,
)
from schemas.user_schema import User
from services.skill_assessment_service import (
    calculate_result,
    extract_candidate_skills,
    generate_assessment_questions,
    next_difficulty,
    question_for,
)
from utils.skill_extractor import normalize_skill
from repositories.job_repository import get_latest_job_description

router = APIRouter()


def public_question(question: dict) -> AssessmentQuestion:
    return AssessmentQuestion.model_validate({key: value for key, value in question.items() if key != "answer"})


@router.post("/skills/extract", response_model=SkillProfile)
async def extract_skills(resume_id: str | None = None, current_user: User = Depends(get_current_user)):
    resume = await get_resume_by_id(resume_id, current_user.id) if resume_id else None
    if not resume:
        resumes = await get_resumes_by_user(current_user.id)
        resume = resumes[0] if resumes else None
    if not resume:
        raise HTTPException(status_code=404, detail="Upload a resume before extracting skills")
    skills = await upsert_candidate_skills(current_user.id, extract_candidate_skills(resume))
    return {"skills": skills}


@router.get("/skills", response_model=SkillProfile)
async def get_skills(current_user: User = Depends(get_current_user)):
    return {"skills": await list_candidate_skills(current_user.id)}


@router.post("/skills", response_model=SkillProfile)
async def add_skills(request: SkillSelection, current_user: User = Depends(get_current_user)):
    skills = [
        {"skill": normalize_skill(skill), "category": "Candidate added", "sources": ["Candidate"], "occurrences": 1}
        for skill in request.skills if skill.strip()
    ]
    if not skills:
        raise HTTPException(status_code=400, detail="Add at least one non-empty skill")
    return {"skills": await upsert_candidate_skills(current_user.id, skills)}


@router.post("/skill-assessment/start", response_model=AssessmentStartResponse)
async def start_assessment(request: AssessmentStart, current_user: User = Depends(get_current_user)):
    skill = request.skill.strip()
    candidate_skill = await get_candidate_skill(current_user.id, skill)
    if not candidate_skill:
        raise HTTPException(status_code=404, detail="Select a skill detected from your resume")
    questions = await generate_assessment_questions(skill, request.self_reported_level, request.reassessment)
    question = questions[0]
    question["difficulty"] = request.self_reported_level
    session = await save_session({
        "user_id": current_user.id,
        "skill": skill,
        "reassessment": request.reassessment,
        "started_at": datetime.utcnow(),
        "current_question": question,
        "questions": questions,
        "self_reported_level": request.self_reported_level,
        "question_index": 0,
        "answers": [],
        "correct_streak": 0,
        "incorrect_streak": 0,
        "difficulty": "Beginner",
        "used_question_ids": [question["id"]],
    })
    return {
        "assessment_id": session["id"],
        "skill": skill,
        "total_questions": 10,
        "question": public_question(question),
    }


@router.post("/skill-assessment/{assessment_id}/answer", response_model=AssessmentStartResponse | AssessmentResult)
async def answer_assessment(
    assessment_id: str,
    request: AssessmentAnswer,
    current_user: User = Depends(get_current_user),
):
    session = await get_session(assessment_id, current_user.id)
    if not session or session.get("completed_at"):
        raise HTTPException(status_code=404, detail="Assessment session not found or already completed")
    question = session.get("current_question")
    if not question or question["id"] != request.question_id:
        raise HTTPException(status_code=400, detail="This question is no longer active")
    if request.answer >= len(question["options"]):
        raise HTTPException(status_code=400, detail="Answer option is out of range")
    correct = request.answer == question["answer"]
    answers = session["answers"] + [{
        "question_id": question["id"],
        "topic": question["topic"],
        "difficulty": question["difficulty"],
        "correct": correct,
    }]
    correct_streak = session["correct_streak"] + 1 if correct else 0
    incorrect_streak = session["incorrect_streak"] + 1 if not correct else 0
    if len(answers) >= 10:
        result = await save_assessment(calculate_result(
            {**session, "answers": answers},
            int((datetime.utcnow() - session["started_at"]).total_seconds()),
        ))
        await update_session(assessment_id, current_user.id, {"answers": answers, "completed_at": datetime.utcnow()})
        await update_candidate_skill(current_user.id, session["skill"], {
            "current_level": result["level"],
            "latest_score": result["score"],
            "last_assessed": result["created_at"],
        })
        return result
    difficulty = next_difficulty(session["difficulty"], correct, correct_streak, incorrect_streak)
    next_question = session["questions"][len(answers)]
    next_question = {**next_question, "difficulty": difficulty}
    updated = await update_session(assessment_id, current_user.id, {
        "answers": answers,
        "current_question": next_question,
        "question_index": len(answers),
        "correct_streak": correct_streak,
        "incorrect_streak": incorrect_streak,
        "difficulty": difficulty,
        "used_question_ids": session["used_question_ids"] + [next_question["id"]],
    })
    return {
        "assessment_id": updated["id"],
        "skill": updated["skill"],
        "total_questions": 10,
        "question": public_question(updated["current_question"]),
    }


@router.get("/skill-assessment/{skill}/latest", response_model=AssessmentResult)
async def latest_assessment(skill: str, current_user: User = Depends(get_current_user)):
    result = await get_latest_assessment(current_user.id, skill)
    if not result:
        raise HTTPException(status_code=404, detail="No completed assessment found")
    return result


@router.get("/skill-assessment/{skill}/history", response_model=list[AssessmentResult])
async def assessment_history(skill: str, current_user: User = Depends(get_current_user)):
    return await list_assessments(current_user.id, skill)


@router.get("/skill-assessment/history", response_model=list[AssessmentResult])
async def all_assessment_history(current_user: User = Depends(get_current_user)):
    return await list_assessments(current_user.id)


@router.get("/skill-profile", response_model=SkillProfile)
async def skill_profile(current_user: User = Depends(get_current_user)):
    return {"skills": await list_candidate_skills(current_user.id)}


@router.get("/skill-profile/priorities", response_model=SkillPriorityResponse)
async def skill_priorities(current_user: User = Depends(get_current_user)):
    candidates = await list_candidate_skills(current_user.id)
    latest = {item["skill"]: item for item in await get_latest_assessments(current_user.id)}
    jd = await get_latest_job_description(current_user.id)
    extracted = (jd or {}).get("extracted_data") or {}
    required = {
        normalize_skill(value)
        for key in ("required_skills", "skills", "technical_skills")
        for value in (extracted.get(key) or [])
        if isinstance(value, str)
    }
    priorities = []
    for candidate in candidates:
        result = latest.get(candidate["skill"], {})
        level = result.get("level") or candidate.get("current_level")
        required_by_jd = candidate["skill"] in required
        if level == "Beginner":
            priority = "High"
        elif level == "Basic" or (required_by_jd and level == "Intermediate"):
            priority = "Medium"
        else:
            priority = "Low"
        priorities.append({
            "skill": candidate["skill"],
            "level": level,
            "score": result.get("score") or candidate.get("latest_score"),
            "required_by_jd": required_by_jd,
            "priority": priority,
            "weak_topics": result.get("weak_topics", []),
        })
    return {"skills": sorted(priorities, key=lambda item: {"High": 0, "Medium": 1, "Low": 2}[item["priority"]])}


@router.post("/learning-roadmap/from-assessment")
async def roadmap_skills(current_user: User = Depends(get_current_user)):
    priorities = await skill_priorities(current_user)
    return {"skills": [item.model_dump() for item in priorities.skills if item.priority in {"High", "Medium"}]}
