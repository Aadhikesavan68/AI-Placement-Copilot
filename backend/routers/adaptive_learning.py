from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from repositories.adaptive_learning_repository import (
    get_mock_test,
    get_plan,
    get_plan_for_analysis,
    save_mock_test,
    save_plan,
    update_mock_test,
    update_plan,
)
from repositories.analysis_repository import get_ats_analysis_by_id
from routers.auth import get_current_user
from schemas.adaptive_learning_schema import (
    LearningPlanCreate,
    LearningPlanResponse,
    LearningSessionCreate,
    MockQuestion,
    MockTestResponse,
    MockTestResult,
    MockTestSubmit,
    TaskUpdate,
)
from schemas.user_schema import User
from services.adaptive_learning_service import (
    build_tasks,
    calculate_progress,
    calculate_streak,
    generate_questions,
)

router = APIRouter()


def _public_plan(plan: dict) -> dict:
    progress = calculate_progress(plan["tasks"], plan["skills"])
    plan.update(progress)
    plan["total_sessions"] = len(plan["tasks"])
    plan["streak_days"] = calculate_streak(plan["tasks"])
    return plan


@router.post("/plans", response_model=LearningPlanResponse)
async def create_learning_plan(
    request: LearningPlanCreate,
    current_user: User = Depends(get_current_user),
):
    analysis = await get_ats_analysis_by_id(request.analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    skills = request.missing_skills or analysis.get("missing_skills", [])
    existing = await get_plan_for_analysis(request.analysis_id, current_user.id)
    if existing:
        raise HTTPException(status_code=409, detail="A learning plan already exists for this analysis")
    try:
        skill_meta, tasks = build_tasks(
            skills, request.start_date, request.target_date,
            request.learning_days, request.daily_minutes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    now = datetime.utcnow()
    plan = {
        "user_id": current_user.id,
        "analysis_id": request.analysis_id,
        "daily_minutes": request.daily_minutes,
        "learning_days": request.learning_days,
        # MongoDB BSON supports datetime, but not Python date objects.
        "start_date": request.start_date.isoformat(),
        "target_date": request.target_date.isoformat(),
        "skills": skill_meta,
        "tasks": tasks,
        "mock_tests": [],
        "created_at": now,
        "updated_at": now,
    }
    return _public_plan(await save_plan(plan))


@router.get("/plans/{plan_id}", response_model=LearningPlanResponse)
async def read_learning_plan(plan_id: str, current_user: User = Depends(get_current_user)):
    plan = await get_plan(plan_id, current_user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    return _public_plan(plan)


@router.get("/plans/by-analysis/{analysis_id}", response_model=LearningPlanResponse)
async def read_learning_plan_by_analysis(analysis_id: str, current_user: User = Depends(get_current_user)):
    plan = await get_plan_for_analysis(analysis_id, current_user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    return _public_plan(plan)


@router.patch("/plans/{plan_id}/tasks/{task_id}", response_model=LearningPlanResponse)
async def update_task(
    plan_id: str,
    task_id: str,
    request: TaskUpdate,
    current_user: User = Depends(get_current_user),
):
    plan = await get_plan(plan_id, current_user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    task = next((item for item in plan["tasks"] if item["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = request.status
    if request.actual_minutes is not None:
        task["actual_minutes"] = request.actual_minutes
    if request.status == "completed":
        task["completed_at"] = datetime.utcnow()
    updated = await update_plan(plan_id, current_user.id, {"tasks": plan["tasks"], "updated_at": datetime.utcnow()})
    return _public_plan(updated or plan)


@router.post("/plans/{plan_id}/sessions", response_model=LearningPlanResponse)
async def record_session(
    plan_id: str,
    request: LearningSessionCreate,
    current_user: User = Depends(get_current_user),
):
    plan = await get_plan(plan_id, current_user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    task = next((item for item in plan["tasks"] if item["id"] == request.task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["actual_minutes"] = min(task["planned_minutes"], task.get("actual_minutes", 0) + request.minutes)
    if task["actual_minutes"] >= task["planned_minutes"]:
        task["status"] = "completed"
        task["completed_at"] = datetime.utcnow()
    elif task["actual_minutes"] > 0:
        task["status"] = "started"
    updated = await update_plan(plan_id, current_user.id, {"tasks": plan["tasks"], "updated_at": datetime.utcnow()})
    return _public_plan(updated or plan)


@router.post("/plans/{plan_id}/tests/{skill}", response_model=MockTestResponse)
async def create_mock_test(plan_id: str, skill: str, current_user: User = Depends(get_current_user)):
    plan = await get_plan(plan_id, current_user.id)
    if not plan or skill not in {item["skill"] for item in plan["skills"]}:
        raise HTTPException(status_code=404, detail="Skill or learning plan not found")
    questions = generate_questions(skill)
    test = {
        "user_id": current_user.id,
        "plan_id": plan_id,
        "skill": skill,
        "questions": questions,
        "status": "in_progress",
        "created_at": datetime.utcnow(),
    }
    saved = await save_mock_test(test)
    return {**saved, "questions": [MockQuestion.model_validate(item) for item in questions]}


@router.post("/tests/{test_id}/submit", response_model=MockTestResult)
async def submit_mock_test(
    test_id: str,
    request: MockTestSubmit,
    current_user: User = Depends(get_current_user),
):
    test = await get_mock_test(test_id, current_user.id)
    if not test:
        raise HTTPException(status_code=404, detail="Mock test not found")
    if test["status"] == "completed":
        raise HTTPException(status_code=409, detail="Mock test has already been submitted")
    if len(request.answers) != len(test["questions"]):
        raise HTTPException(status_code=400, detail="Answer one option for every question")
    correct = sum(
        answer == question["answer"]
        for answer, question in zip(request.answers, test["questions"])
    )
    score = round(correct / len(test["questions"]) * 100)
    weak_topics = [
        question["topic"]
        for answer, question in zip(request.answers, test["questions"])
        if answer != question["answer"]
    ]
    submitted_at = datetime.utcnow()
    result = await update_mock_test(test_id, current_user.id, {
        "status": "completed",
        "score": score,
        "weak_topics": list(dict.fromkeys(weak_topics)),
        "submitted_at": submitted_at,
    })
    if result:
        plan = await get_plan(result["plan_id"], current_user.id)
        if plan:
            for skill in plan["skills"]:
                if skill["skill"] == result["skill"]:
                    skill["weak_topics"] = list(dict.fromkeys(
                        skill.get("weak_topics", []) + weak_topics
                    ))
            for task in plan["tasks"]:
                if task["skill"] == result["skill"] and task["status"] == "planned" and weak_topics:
                    task["description"] = (
                        f"Review weak topics ({', '.join(weak_topics)}) before completing this exercise."
                    )
            plan["mock_tests"] = plan.get("mock_tests", []) + [{
                "test_id": result["id"],
                "skill": result["skill"],
                "score": score,
                "weak_topics": list(dict.fromkeys(weak_topics)),
                "submitted_at": submitted_at,
            }]
            await update_plan(result["plan_id"], current_user.id, {
                "mock_tests": plan["mock_tests"],
                "skills": plan["skills"],
                "tasks": plan["tasks"],
                "updated_at": submitted_at,
            })
    return {
        "id": test_id,
        "skill": test["skill"],
        "score": score,
        "total": len(test["questions"]),
        "weak_topics": list(dict.fromkeys(weak_topics)),
        "submitted_at": submitted_at,
    }
