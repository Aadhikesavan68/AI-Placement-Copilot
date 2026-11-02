import copy
import json
import os
import re

import httpx

from services.resume_service import calculate_completion_score

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

EDITABLE_FIELDS = [
    "summary", "skills", "languages_prog", "frameworks", "databases", "cloud",
    "tools", "soft_skills", "education", "projects", "experience", "internships",
    "certifications", "achievements", "languages", "technologies",
]


def _clean_sentence(value: str) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"^[•*\-]+\s*", "", value)
    if value and value[0].islower():
        value = value[0].upper() + value[1:]
    return value


def _fallback_resume(resume: dict) -> dict:
    corrected = copy.deepcopy(resume)
    replacements = {
        r"\brecieve\b": "receive", r"\bdevelopement\b": "development",
        r"\bprograming\b": "programming", r"\bexperiance\b": "experience",
        r"\bmanagment\b": "management", r"\bresponsibilites\b": "responsibilities",
        r"\bacheivements\b": "achievements", r"\bteh\b": "the",
    }
    for field in EDITABLE_FIELDS:
        value = corrected.get(field)
        if isinstance(value, str):
            for pattern, replacement in replacements.items():
                value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
            corrected[field] = _clean_sentence(value)
        elif isinstance(value, list):
            cleaned = []
            for item in value:
                if isinstance(item, str):
                    for pattern, replacement in replacements.items():
                        item = re.sub(pattern, replacement, item, flags=re.IGNORECASE)
                    item = _clean_sentence(item)
                cleaned.append(item)
            corrected[field] = list(dict.fromkeys(cleaned))
    return corrected


def _diffs(original: dict, corrected: dict) -> list:
    issues = []
    for field in EDITABLE_FIELDS:
        before = original.get(field)
        after = corrected.get(field)
        if before != after:
            label = field.replace("_", " ").title()
            issues.append({
                "section": label,
                "before": before,
                "after": after,
                "type": "grammar and presentation",
            })
    return issues


async def improve_resume(resume: dict) -> dict:
    original = copy.deepcopy(resume)
    corrected = None
    provider = "deterministic"
    prompt = f"""
You are a professional resume editor. Correct spelling, grammar, punctuation, clarity,
consistent tense, and presentation in this parsed resume. Keep every factual claim,
contact detail, skill, date, employer, title, and metric. Do not invent content.
Return ONLY valid JSON with exactly these editable fields, preserving each field's type:
{json.dumps(EDITABLE_FIELDS)}
For list fields, return concise, consistent resume bullets. For summary, return a string.
RESUME:
{json.dumps({field: resume.get(field) for field in EDITABLE_FIELDS}, indent=2)}
"""
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            if GEMINI_API_KEY:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
                    json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}},
                )
                if response.status_code == 200:
                    raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                    corrected = json.loads(raw)
                    provider = "AI"
            elif OPENAI_API_KEY:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "Return JSON only."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}},
                )
                if response.status_code == 200:
                    corrected = json.loads(response.json()["choices"][0]["message"]["content"])
                    provider = "AI"
    except Exception as exc:
        print(f"Resume improvement AI failed: {exc}")

    if not isinstance(corrected, dict):
        corrected = _fallback_resume(resume)

    # Only accept known fields and retain the parsed value if the model omitted one.
    for field in EDITABLE_FIELDS:
        if field not in corrected or not isinstance(corrected[field], (str, list)):
            corrected[field] = original.get(field)
    issues = _diffs(original, corrected)
    return {
        "provider": provider,
        "issues_found": len(issues),
        "issues": issues,
        "presentation_updates": [
            "Standardized section wording and bullet formatting.",
            "Kept factual content and contact information unchanged.",
        ],
        "resume": corrected,
        "completion_score": calculate_completion_score(corrected),
    }