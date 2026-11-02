from datetime import date, datetime, timedelta
from math import ceil
from typing import Iterable


DIFFICULTY_HOURS = {"Beginner": 8, "Intermediate": 14, "Advanced": 22}


def _skill_meta(skill: str, index: int) -> dict:
    difficulty = "Intermediate"
    lowered = skill.lower()
    if any(term in lowered for term in ("basic", "html", "css")):
        difficulty = "Beginner"
    elif any(term in lowered for term in ("system design", "architecture", "kubernetes", "aws")):
        difficulty = "Advanced"
    return {
        "skill": skill,
        "difficulty": difficulty,
        "estimated_hours": DIFFICULTY_HOURS[difficulty],
        "priority": "High" if index == 0 else ("Medium" if index < 3 else "Low"),
        "planned_minutes": 0,
        "completed_minutes": 0,
        "confidence": 0,
        "weak_topics": [],
    }


def _study_dates(start: date, target: date, weekdays: Iterable[int]) -> list[date]:
    allowed = set(weekdays)
    current = start
    dates = []
    while current <= target:
        if current.weekday() in allowed:
            dates.append(current)
        current += timedelta(days=1)
    return dates


def build_tasks(
    skills: list[str],
    start_date: date,
    target_date: date,
    learning_days: list[int],
    daily_minutes: int,
) -> tuple[list[dict], list[dict]]:
    clean_skills = list(dict.fromkeys(skill.strip() for skill in skills if skill.strip()))
    if not clean_skills:
        return [], []

    metas = [_skill_meta(skill, index) for index, skill in enumerate(clean_skills)]
    study_dates = _study_dates(start_date, target_date, learning_days)
    if not study_dates:
        raise ValueError("The selected date range contains no selected learning days")

    total_minutes = len(study_dates) * daily_minutes
    weights = [meta["estimated_hours"] for meta in metas]
    allocated = [total_minutes * weight // sum(weights) for weight in weights]
    for index in range(total_minutes - sum(allocated)):
        allocated[index % len(allocated)] += 1

    tasks = []
    task_index = 0
    for skill_index, (meta, skill_minutes) in enumerate(zip(metas, allocated)):
        meta["planned_minutes"] = skill_minutes
        minutes_left = skill_minutes
        while minutes_left > 0 and task_index < len(study_dates):
            task_minutes = min(daily_minutes, minutes_left)
            task_date = study_dates[task_index]
            tasks.append({
                "id": f"task-{task_date.isoformat()}-{skill_index}-{task_index}",
                "date": task_date.isoformat(),
                "skill": meta["skill"],
                "title": f"{meta['skill']}: focused practice",
                "description": f"Study the core concepts of {meta['skill']} and complete a small hands-on exercise.",
                "planned_minutes": task_minutes,
                "actual_minutes": 0,
                "status": "planned",
                "completed_at": None,
            })
            minutes_left -= task_minutes
            task_index += 1
        if minutes_left > 0:
            # Capacity is exhausted; keep the plan honest instead of silently exceeding the user's limit.
            meta["planned_minutes"] -= minutes_left

    return metas, tasks


def calculate_progress(tasks: list[dict], skills: list[dict]) -> dict:
    planned = sum(task.get("planned_minutes", 0) for task in tasks)
    completed = sum(
        task.get("actual_minutes", 0) for task in tasks
        if task.get("status") == "completed"
    )
    completed_tasks = {task["skill"] for task in tasks if task.get("status") == "completed"}
    for skill in skills:
        skill["completed_minutes"] = sum(
            task.get("actual_minutes", 0) for task in tasks if task.get("skill") == skill["skill"]
        )
        skill["confidence"] = min(
            100,
            round((skill["completed_minutes"] / skill["planned_minutes"]) * 100)
            if skill["planned_minutes"] else 0,
        )
    return {
        "total_planned_minutes": planned,
        "completed_minutes": completed,
        "progress_percent": round((completed / planned) * 100, 1) if planned else 0,
        "completed_tasks": len(completed_tasks),
    }


def calculate_streak(tasks: list[dict]) -> int:
    completed_dates = {
        date.fromisoformat(task["date"])
        for task in tasks
        if task.get("status") == "completed"
    }
    streak = 0
    current = date.today()
    while current in completed_dates:
        streak += 1
        current -= timedelta(days=1)
    return streak


def generate_questions(skill: str) -> list[dict]:
    return [
        {
            "question": f"Which approach is most useful when learning {skill}?",
            "options": ["Read without practice", "Combine concepts with a small exercise", "Skip fundamentals", "Only memorize syntax"],
            "answer": 1,
            "topic": "fundamentals",
        },
        {
            "question": f"What should you do when a {skill} problem remains unclear?",
            "options": ["Record the gap and revisit it", "Ignore it permanently", "Guess and stop", "Delete your notes"],
            "answer": 0,
            "topic": "problem solving",
        },
        {
            "question": f"How can progress in {skill} be verified?",
            "options": ["By opening a course page", "By spending time only", "By completing an applied task or assessment", "By skipping review"],
            "answer": 2,
            "topic": "assessment",
        },
    ]
