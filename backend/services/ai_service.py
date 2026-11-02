import os
import json
import httpx
from typing import Optional
from services.ats_service import compare_resume_and_jd, parse_job_description_text

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

async def run_ai_analysis(resume_data: dict, jd_text: str, file_type: str = "pdf") -> dict:
    """Runs ATS comparison analysis. Uses Gemini/OpenAI if key is present, otherwise falls back to deterministic analysis."""
    # First parse JD text
    jd_data = parse_job_description_text(jd_text)
    
    # Check if we should use LLM
    if not GEMINI_API_KEY and not OPENAI_API_KEY:
        # Fallback to deterministic scoring
        print("Using deterministic ATS scoring engine (no API keys found)")
        analysis = compare_resume_and_jd(resume_data, jd_data, file_type)
        return analysis, jd_data

    # We have API keys! Let's build the prompt
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) Resume Analyzer.
    Compare the following Resume details with the Job Description.

    RESUME DETAILS:
    {json.dumps(resume_data, indent=2)}

    JOB DESCRIPTION:
    {jd_text}

    Generate a detailed ATS comparison report.
    You MUST output your response in valid JSON matching the following structure.
    Do NOT wrap in markdown code blocks like ```json. Return ONLY raw JSON text.

    EXPECTED JSON STRUCTURE:
    {{
        "ats_score": 75, // 0-100
        "match_score": 82, // 0-100
        "scores": {{
            "skill_match": 80,
            "experience_match": 75,
            "education_match": 100,
            "keyword_match": 70,
            "responsibilities_match": 85,
            "project_relevance": 90
        }},
        "ats_details": {{
            "formatting": 100,
            "section_presence": 90,
            "keyword_optimization": 80,
            "readability": 85,
            "contact_information": 100,
            "projects": 90,
            "experience": 80,
            "education": 100,
            "achievements": 75,
            "skills": 95,
            "action_verbs": 80,
            "resume_length": 100,
            "consistency": 90
        }},
        "missing_skills": ["Docker", "Kubernetes", "AWS"],
        "suggestions": ["Add Docker container experience", "Include measurable metrics in project descriptions"],
        "keywords": {{
            "existing_keywords": ["Python", "React", "SQL"],
            "missing_keywords": ["CI/CD", "Docker", "AWS"],
            "recommended_keywords": ["FastAPI", "React", "MongoDB", "Docker"]
        }},
        "ai_suggestions": ["Your resume matches 82% of the JD. Highlight cloud/deployment skills like Docker/AWS to boost relevance."],
        "highlights": {{
            "good_sections": ["Experience", "Education", "Skills"],
            "weak_sections": ["Projects"],
            "missing_sections": ["Achievements"]
        }},
        "roadmap": [
            {{
                "week": 1,
                "topic": "Learn Docker",
                "description": "Understand containerization concepts, write Dockerfiles, and containerize a web application.",
                "resources": [
                    {{
                        "course_name": "Docker and Kubernetes: The Complete Guide",
                        "provider": "Udemy",
                        "difficulty": "Beginner",
                        "estimated_duration": "20h",
                        "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/"
                    }}
                ]
            }}
        ]
    }}
    """

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            if GEMINI_API_KEY:
                print("Running Gemini AI ATS comparison...")
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "responseMimeType": "application/json"
                    }
                }
                res = await client.post(gemini_url, json=payload)
                if res.status_code == 200:
                    result = res.json()
                    raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    parsed_json = json.loads(raw_text)
                    return parsed_json, jd_data
                else:
                    print(f"Gemini API returned error {res.status_code}: {res.text}")
                    
            if OPENAI_API_KEY:
                print("Running OpenAI AI ATS comparison...")
                openai_url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a helpful ATS resume scoring assistant. Return JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
                res = await client.post(openai_url, headers=headers, json=payload)
                if res.status_code == 200:
                    result = res.json()
                    raw_text = result["choices"][0]["message"]["content"]
                    parsed_json = json.loads(raw_text)
                    return parsed_json, jd_data
                else:
                    print(f"OpenAI API returned error {res.status_code}: {res.text}")

    except Exception as e:
        print(f"AI comparison failed due to: {e}. Falling back to deterministic analysis.")
        
    # Final fallback
    analysis = compare_resume_and_jd(resume_data, jd_data, file_type)
    return analysis, jd_data
