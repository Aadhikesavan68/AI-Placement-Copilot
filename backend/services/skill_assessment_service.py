from collections import defaultdict
import json
import re
import uuid
import httpx

from utils.resume_parser import (
    CLOUD_INFRA,
    DATABASES,
    DEVELOPER_TOOLS,
    FRAMEWORKS,
    LANGUAGES_PROG,
)
from utils.skill_extractor import normalize_skill
from core.config import settings

LEVELS = ["Beginner", "Basic", "Intermediate", "Advanced"]
DIFFICULTIES = ["Beginner", "Basic", "Intermediate", "Advanced"]

QUESTION_BANK = {
    "Python": [
        ("Fundamentals", "variables", "Beginner", "Which collection stores ordered, mutable values?", ["Tuple", "List", "Set", "String"], 1),
        ("Functions", "functions", "Basic", "What does a Python function return when it reaches the end without return?", ["0", "False", "None", "It raises an error"], 2),
        ("Data Structures", "dictionaries", "Intermediate", "What is the average lookup complexity for a key in a Python dictionary?", ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 0),
        ("Debugging", "exceptions", "Advanced", "Which construct guarantees cleanup code runs after a try block?", ["catch", "finally", "else", "assert"], 1),
    ],
    "Java": [
        ("Fundamentals", "types", "Beginner", "Which type stores a whole number in Java?", ["boolean", "int", "char[]", "float[]"], 1),
        ("OOP", "polymorphism", "Basic", "Which feature lets a subclass provide a specific implementation of a parent method?", ["Overloading", "Overriding", "Encapsulation", "Casting"], 1),
        ("Collections", "collections", "Intermediate", "Which collection stores key-value pairs?", ["List", "Set", "Map", "Queue"], 2),
        ("Exceptions", "exceptions", "Advanced", "Which keyword declares checked exceptions a method may throw?", ["throws", "throwable", "raise", "except"], 0),
    ],
    "C++": [
        ("Fundamentals", "references", "Beginner", "Which symbol declares a reference?", ["*", "&", "#", "::"], 1),
        ("STL", "vector", "Basic", "Which STL container provides a dynamic contiguous array?", ["map", "vector", "set", "stack"], 1),
        ("Memory", "pointers", "Intermediate", "What does delete do for a pointer created with new?", ["Copies it", "Releases its object", "Makes it const", "Moves it"], 1),
        ("OOP", "polymorphism", "Advanced", "Which mechanism enables runtime dispatch through a base pointer?", ["Templates", "Virtual functions", "Namespaces", "Macros"], 1),
    ],
    "SQL": [
        ("Queries", "select", "Beginner", "Which clause filters rows before grouping?", ["WHERE", "HAVING", "ORDER BY", "LIMIT"], 0),
        ("Aggregation", "group by", "Basic", "Which clause groups rows for aggregate calculations?", ["SORT", "GROUP BY", "PARTITION", "MERGE"], 1),
        ("Joins", "joins", "Intermediate", "Which join returns matching rows from both tables?", ["INNER JOIN", "FULL JOIN", "CROSS JOIN", "LEFT JOIN"], 0),
        ("Optimization", "indexes", "Advanced", "What is a common trade-off of adding an index?", ["Faster writes", "More storage and write cost", "Less storage", "No query planning"], 1),
    ],
    "React": [
        ("Components", "components", "Beginner", "What syntax is commonly used to describe UI in React?", ["JSX", "SQL", "YAML", "Bash"], 0),
        ("Props", "props", "Basic", "Are React props normally mutated by the receiving component?", ["Yes", "No", "Only in production", "Only with TypeScript"], 1),
        ("Hooks", "useEffect", "Intermediate", "Which hook is used for synchronizing with an external system?", ["useMemo", "useRef", "useEffect", "useId"], 2),
        ("Performance", "memoization", "Advanced", "What can React.memo help avoid?", ["All network calls", "Some unnecessary child renders", "All state updates", "Every effect"], 1),
    ],
}

GENERIC_QUESTIONS = [
    ("Fundamentals", "core concepts", "Beginner", "What is the safest way to build proficiency in a technical skill?", ["Memorize terms only", "Combine concepts with practical exercises", "Skip fundamentals", "Avoid feedback"], 1),
    ("Problem Solving", "problem solving", "Basic", "What is the best response when an implementation does not work?", ["Ignore it", "Record the failure and isolate the cause", "Delete the project", "Guess repeatedly"], 1),
    ("Practical Use", "application", "Intermediate", "Which evidence best demonstrates applied skill?", ["A keyword in a resume", "A completed, testable implementation", "A course title", "A copied snippet"], 1),
    ("Quality", "testing", "Advanced", "Why should technical changes be validated with tests?", ["To make code longer", "To detect regressions and verify behavior", "To avoid documentation", "To remove all edge cases"], 1),
]


def extract_candidate_skills(resume: dict) -> list[dict]:
    fields = {
        "skills": "Skills Section",
        "languages_prog": "Programming",
        "frameworks": "Frameworks",
        "databases": "Databases",
        "cloud": "Cloud",
        "tools": "Tools",
        "technologies": "Projects / Experience",
    }
    known_technical = {
        normalize_skill(value)
        for value in LANGUAGES_PROG + FRAMEWORKS + DATABASES + CLOUD_INFRA + DEVELOPER_TOOLS
    }
    found: dict[str, dict] = {}
    for field, source in fields.items():
        values = resume.get(field) or []
        if isinstance(values, str):
            values = re.split(r"[,;\n|]", values)
        for value in values:
            if not isinstance(value, str) or not value.strip():
                continue
            skill = normalize_skill(value)
            if field == "skills" and skill not in known_technical:
                continue
            if len(skill) < 2:
                continue
            item = found.setdefault(skill, {"skill": skill, "category": source, "sources": [], "occurrences": 0})
            item["occurrences"] += 1
            if source not in item["sources"]:
                item["sources"].append(source)
    return list(found.values())


def question_for(skill: str, index: int, used_ids: set[str]) -> dict:
    normalized = normalize_skill(skill)
    bank = QUESTION_BANK.get(normalized, GENERIC_QUESTIONS)
    template = bank[index % len(bank)]
    category, topic, difficulty, question, options, answer = template
    question_id = f"{uuid.uuid4()}"
    while question_id in used_ids:
        question_id = f"{uuid.uuid4()}"
    return {
        "id": question_id,
        "skill": normalized,
        "category": category,
        "topic": topic,
        "difficulty": difficulty,
        "question": question,
        "options": options,
        "answer": answer,
        "sequence": index + 1,
    }


def _fallback_questions(skill: str, level: str, reassessment: bool) -> list[dict]:
    questions = []
    bank = QUESTION_BANK.get(normalize_skill(skill), GENERIC_QUESTIONS)
    start = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}[level]
    for index in range(10):
        template = bank[(index + start + (4 if reassessment else 0)) % len(bank)]
        category, topic, difficulty, question, options, answer = template
        questions.append({
            "id": str(uuid.uuid4()),
            "category": category,
            "topic": topic,
            "difficulty": level if index < 3 else difficulty,
            "question": question,
            "options": options,
            "answer": answer,
            "sequence": index + 1,
        })
    return questions


async def generate_assessment_questions(skill: str, level: str, reassessment: bool = False) -> list[dict]:
    """Generate an objectively scorable question set, with a safe local fallback."""
    fallback = _fallback_questions(skill, level, reassessment)
    if not settings.GEMINI_API_KEY:
        return fallback

    prompt = f"""
Create exactly 10 multiple-choice questions for a {skill} assessment.
The candidate self-reported level is {level}. Questions must be appropriate for that level,
cover different topics, have exactly one correct answer, and be objectively gradable.
Use new questions because this is {"a reassessment" if reassessment else "the first assessment"}.
Return ONLY a JSON array. Each item must have:
category, topic, difficulty, question, options (exactly 4 strings), answer (0-3).
Do not include explanations, markdown, or answer hints.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(f"{url}?key={settings.GEMINI_API_KEY}", json=payload)
            response.raise_for_status()
            raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            generated = json.loads(raw)
            if not isinstance(generated, list) or len(generated) != 10:
                raise ValueError("Gemini did not return exactly 10 questions")
            validated = []
            for index, item in enumerate(generated):
                if (
                    not isinstance(item, dict)
                    or not isinstance(item.get("options"), list)
                    or len(item["options"]) != 4
                    or not isinstance(item.get("answer"), int)
                    or not 0 <= item["answer"] < 4
                ):
                    raise ValueError("Gemini returned an invalid question shape")
                validated.append({
                    "id": str(uuid.uuid4()),
                    "category": str(item.get("category", "Technical")),
                    "topic": str(item.get("topic", "Core concepts")),
                    "difficulty": str(item.get("difficulty", level)),
                    "question": str(item["question"]),
                    "options": [str(option) for option in item["options"]],
                    "answer": item["answer"],
                    "sequence": index + 1,
                })
            return validated
    except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Gemini assessment generation failed; using local question bank: {exc}")
        return fallback


def next_difficulty(current: str, correct: bool, correct_streak: int, incorrect_streak: int) -> str:
    index = DIFFICULTIES.index(current)
    if correct and correct_streak >= 2:
        return DIFFICULTIES[min(index + 1, len(DIFFICULTIES) - 1)]
    if not correct and incorrect_streak >= 2:
        return DIFFICULTIES[max(index - 1, 0)]
    return current


def calculate_result(session: dict, time_taken_seconds: int) -> dict:
    answers = session["answers"]
    total = len(answers)
    correct = sum(item["correct"] for item in answers)
    score = round(correct / total * 100) if total else 0
    topic_totals: dict[str, list[int]] = defaultdict(list)
    for item in answers:
        topic_totals[item["topic"]].append(int(item["correct"]))
    topic_scores = {topic: round(sum(values) / len(values) * 100) for topic, values in topic_totals.items()}
    weak = [topic for topic, value in topic_scores.items() if value < 60]
    strong = [topic for topic, value in topic_scores.items() if value >= 75]
    reached_index = max(DIFFICULTIES.index(item["difficulty"]) for item in answers)
    level_index = min(reached_index, max(0, score // 25 - 1))
    level = LEVELS[level_index]
    return {
        "user_id": session["user_id"],
        "skill": session["skill"],
        "score": score,
        "level": level,
        "total_questions": total,
        "correct_answers": correct,
        "difficulty_reached": DIFFICULTIES[reached_index],
        "topic_scores": topic_scores,
        "weak_topics": weak,
        "strong_topics": strong,
        "time_taken_seconds": max(0, time_taken_seconds),
    }
