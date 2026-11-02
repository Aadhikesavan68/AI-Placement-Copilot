import os
import re
import shutil
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import UploadFile, HTTPException

from utils.resume_parser import extract_text_from_pdf, extract_text_from_docx
from utils.skill_extractor import normalize_skills
from utils.jd_parser import TECH_KEYWORDS
from repositories.job_repository import (
    create_job_description,
    get_latest_job_description,
    get_job_descriptions_by_user,
    get_job_description_by_id,
    delete_job_description_by_id,
)

UPLOAD_DIR = "uploads"

# Comprehensive tools catalogue
ALL_TOOLS = [
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Trello", "Asana",
    "Slack", "Figma", "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible",
    "Postman", "VSCode", "IntelliJ", "PyCharm", "Eclipse", "Linux", "Unix", "Bash",
    "Webpack", "Vite", "Datadog", "Grafana", "Prometheus", "Selenium", "Cypress",
    "Jest", "Mocha", "PyTest", "PostgreSQL", "MongoDB", "Redis", "Kafka", "RabbitMQ"
]

ALL_SOFT_SKILLS = [
    "Leadership", "Communication", "Teamwork", "Problem Solving", "Time Management",
    "Collaboration", "Adaptability", "Creativity", "Organization", "Critical Thinking",
    "Work Ethic", "Interpersonal Skills", "Mentorship", "Attention to Detail"
]

COMMON_ROLES = [
    "Software Engineer", "Senior Software Engineer", "Full Stack Developer", "Full Stack Engineer",
    "Frontend Developer", "Frontend Engineer", "Backend Developer", "Backend Engineer",
    "DevOps Engineer", "Cloud Engineer", "Cloud Architect", "Data Scientist", "Data Engineer",
    "Machine Learning Engineer", "AI Engineer", "QA Engineer", "Mobile Developer", "iOS Developer",
    "Android Developer", "Site Reliability Engineer", "System Architect", "Product Manager",
    "Technical Lead", "Engineering Manager", "Database Administrator", "Security Engineer"
]

def extract_job_title(jd_text: str) -> str:
    """Extracts job title / role from the job description text."""
    if not jd_text:
        return "Software Engineer"
        
    lines = [line.strip() for line in jd_text.split('\n') if line.strip()]
    if not lines:
        return "Software Engineer"

    # 1. Pattern matching for Title / Role / Position prefixes
    patterns = [
        r'(?:job\s+title|title|role|position|opening\s+for|looking\s+for|hiring\s+for)\s*[:\-–]\s*([A-Za-z0-9\s\.\#\-\+\&\/\(\)]{3,60})',
        r'(?:we\s+are\s+looking\s+for\s+(?:a|an)|hiring\s+(?:a|an))\s+([A-Za-z0-9\s\.\#\-\+\&\/\(\)]{3,60})'
    ]
    for pattern in patterns:
        for line in lines[:10]:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean any trailing punctuation or phrases
                title = re.sub(r'[\.\,\;]+$', '', title).strip()
                if len(title) >= 3 and len(title) <= 60:
                    return title

    # 2. Check if any line in first 6 lines closely matches a standard role title
    for line in lines[:6]:
        cleaned_line = re.sub(r'^[#\*\-\•\d\.\s]+', '', line).strip()
        for role in COMMON_ROLES:
            if role.lower() in cleaned_line.lower() and len(cleaned_line) <= 65:
                return cleaned_line

    # 3. Fallback to first line if reasonably short and descriptive
    if len(lines[0]) <= 50 and not any(char in lines[0] for char in ['@', 'http', '{', '}']):
        return lines[0]

    return "Software Engineer"


def extract_company_name(jd_text: str) -> str:
    """Extracts company name from the job description text."""
    if not jd_text:
        return "Target Company"
        
    patterns = [
        r'(?:about|at)\s+([A-Z][A-Za-z0-9\s\.\,\-\&]{1,35})(?:\s+is\s+a|\s+believes|\s+focuses|\s+we|\s+team|\s+headquartered)',
        r'(?:company|organization)\s*[:\-–]\s*([A-Za-z0-9\s\.\,\-\&]{1,35})',
        r'welcome\s+to\s+([A-Z][A-Za-z0-9\s\.\,\-\&]{1,35})'
    ]
    for pattern in patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            company = match.group(1).strip().rstrip('.,;')
            if company and len(company) > 1:
                return company
    return "Target Company"


def extract_experience(jd_text: str) -> str:
    """Extracts required experience from the job description text."""
    if not jd_text:
        return "0-2 years"
        
    text_lower = jd_text.lower()
    
    # Check specific year ranges
    patterns = [
        r'(\d+\s*(?:to|-)\s*\d+\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:work|relevant|hands-on|industry|professional))?\s*experience)',
        r'(\d+\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:work|relevant|hands-on|industry|professional))?\s*experience)',
        r'(?:minimum|at\s+least)\s*(\d+\+?\s*(?:years?|yrs?))',
        r'experience\s*[:\-–]\s*(\d+\+?\s*(?:years?|yrs?))'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            matched_text = match.group(1).strip()
            # Clean up display format
            return matched_text.capitalize()
            
    # Heuristic level checks
    if "senior" in text_lower or "lead" in text_lower or "principal" in text_lower:
        return "5+ years"
    elif "mid-level" in text_lower or "intermediate" in text_lower:
        return "2-5 years"
    elif "entry level" in text_lower or "junior" in text_lower or "intern" in text_lower or "fresher" in text_lower:
        return "0-2 years"
        
    return "Not specified (0-2 years)"


def extract_education(jd_text: str) -> List[str]:
    """Extracts degree and educational requirements."""
    if not jd_text:
        return ["Bachelor's Degree in Computer Science or related field"]
        
    text_lower = jd_text.lower()
    education = []
    
    degree_mappings = {
        "bachelor": "Bachelor's Degree in Computer Science, Engineering, or related field",
        "b.s": "Bachelor of Science (B.S.) in Computer Science or related field",
        "b.tech": "Bachelor of Technology (B.Tech) in Computer Science/IT or related field",
        "b.e": "Bachelor of Engineering (B.E.) in Computer Science or related field",
        "master": "Master's Degree (M.S. / M.Tech) in Computer Science or related field",
        "m.s": "Master of Science (M.S.) in related discipline",
        "m.tech": "Master of Technology (M.Tech)",
        "phd": "PhD / Doctorate in Computer Science, AI, or related quantitative field",
        "doctorate": "PhD / Doctorate in related quantitative field",
        "diploma": "Associate Degree or Technical Diploma in related field"
    }
    
    for key, desc in degree_mappings.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
            if desc not in education:
                education.append(desc)
                
    if not education:
        if any(term in text_lower for term in ["degree", "computer science", "engineering", "graduate", "university"]):
            education.append("Bachelor's Degree in Computer Science or equivalent practical experience")
        else:
            education.append("Bachelor's Degree in Computer Science, Engineering or related technical field")
            
    return education


def extract_responsibilities(jd_text: str) -> List[str]:
    """Extracts job duties and responsibilities list."""
    if not jd_text:
        return []
        
    lines = jd_text.split('\n')
    responsibilities = []
    in_section = False
    
    resp_headers = [
        "responsibilities", "duties", "what you'll do", "what you will do",
        "key tasks", "role responsibilities", "core responsibilities",
        "what we expect", "day to day", "accountabilities", "the role"
    ]
    other_headers = [
        "requirements", "qualifications", "skills", "experience", "education",
        "preferred", "nice to have", "about us", "benefits", "what we offer", "perks"
    ]
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        test_lower = line_clean.lower()
        
        # Check if this line is a section header
        if len(line_clean) < 50:
            if any(h in test_lower for h in resp_headers):
                in_section = True
                continue
            elif any(h in test_lower for h in other_headers):
                in_section = False
                
        if in_section:
            # Clean bullet points
            cleaned = re.sub(r'^[•\-\*\s\d\.\)\:]+', '', line_clean).strip()
            if cleaned and len(cleaned) > 8:
                responsibilities.append(cleaned)
                
    # Fallback: if no dedicated section found, extract all prominent bullet items
    if not responsibilities:
        for line in lines:
            line_clean = line.strip()
            if (line_clean.startswith('•') or line_clean.startswith('-') or line_clean.startswith('*')) and len(line_clean) > 20:
                cleaned = re.sub(r'^[•\-\*\s\d\.\)]+', '', line_clean).strip()
                if cleaned:
                    responsibilities.append(cleaned)
                    
    return responsibilities[:12]


def extract_skills_and_categories(jd_text: str) -> Dict[str, Any]:
    """
    Extracts Required Skills, Preferred Skills, Technologies, Tools, and Keywords.
    """
    if not jd_text:
        return {
            "required_skills": [],
            "preferred_skills": [],
            "technologies": [],
            "tools": [],
            "keywords": [],
            "soft_skills": []
        }
        
    text_lower = jd_text.lower()
    
    # 1. Identify all matching technical keywords
    detected_skills = []
    for keyword in TECH_KEYWORDS:
        escaped = re.escape(keyword)
        pattern = r'(^|[^a-z0-9])' + escaped + r'([^a-z0-9]|$)'
        if re.search(pattern, text_lower):
            detected_skills.append(keyword)
            
    normalized_tech = normalize_skills(detected_skills)
    
    # 2. Identify Tools
    detected_tools = []
    for tool in ALL_TOOLS:
        pattern = r'(^|[^a-z0-9])' + re.escape(tool.lower()) + r'([^a-z0-9]|$)'
        if re.search(pattern, text_lower):
            detected_tools.append(tool)
            
    # 3. Identify Soft Skills
    detected_soft_skills = []
    for soft in ALL_SOFT_SKILLS:
        pattern = r'(^|[^a-z0-9])' + re.escape(soft.lower()) + r'([^a-z0-9]|$)'
        if re.search(pattern, text_lower):
            detected_soft_skills.append(soft)
            
    # 4. Partition skills into Required and Preferred
    lines = jd_text.split('\n')
    required_skills = []
    preferred_skills = []
    
    in_preferred_section = False
    in_required_section = False
    
    for line in lines:
        line_clean = line.strip().lower()
        if not line_clean:
            continue
            
        if len(line_clean) < 50:
            if any(p in line_clean for p in ["preferred", "nice to have", "good to have", "plus", "bonus", "desirable"]):
                in_preferred_section = True
                in_required_section = False
            elif any(r in line_clean for r in ["required", "minimum qualification", "basic qualification", "must have", "requirements", "core skills"]):
                in_required_section = True
                in_preferred_section = False
                
        # Find which skills are on this line
        line_skills = [s for s in normalized_tech if re.search(r'(^|[^a-z0-9])' + re.escape(s.lower()) + r'([^a-z0-9]|$)', line_clean)]
        for s in line_skills:
            if in_preferred_section:
                if s not in preferred_skills:
                    preferred_skills.append(s)
            else:
                if s not in required_skills:
                    required_skills.append(s)
                    
    # If no partition occurred, allocate all tech to required
    if not required_skills and normalized_tech:
        required_skills = [s for s in normalized_tech if s not in preferred_skills]
    if not required_skills:
        required_skills = normalized_tech.copy()
        
    # Keywords: comprehensive set of unique tech, tools, soft skills, and concepts
    keywords = list(dict.fromkeys(normalized_tech + detected_tools + detected_soft_skills))
    
    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "technologies": normalized_tech,
        "tools": detected_tools,
        "keywords": keywords,
        "soft_skills": detected_soft_skills
    }


def parse_job_description(jd_text: str) -> dict:
    """Legacy helper returning target profile dict for analysis service."""
    data = parse_job_description_complete(jd_text)
    return {
        "company_name": data.get("company_name", "Target Company"),
        "skills": data.get("required_skills", []),
        "preferred_skills": data.get("preferred_skills", []),
        "important_topics": data.get("technologies", [])
    }


def parse_job_description_complete(jd_text: str) -> Dict[str, Any]:
    """
    Extracts all 9 required fields from Job Description text:
    1. Job Title
    2. Required Skills
    3. Preferred Skills
    4. Responsibilities
    5. Experience
    6. Education
    7. Keywords
    8. Technologies
    9. Tools
    """
    job_title = extract_job_title(jd_text)
    company_name = extract_company_name(jd_text)
    experience = extract_experience(jd_text)
    education = extract_education(jd_text)
    responsibilities = extract_responsibilities(jd_text)
    skills_data = extract_skills_and_categories(jd_text)
    
    return {
        "job_title": job_title,
        "role": job_title,
        "company_name": company_name,
        "required_skills": skills_data["required_skills"],
        "preferred_skills": skills_data["preferred_skills"],
        "responsibilities": responsibilities,
        "experience": experience,
        "required_experience": experience,
        "education": education,
        "keywords": skills_data["keywords"],
        "technologies": skills_data["technologies"],
        "tools": skills_data["tools"],
        "soft_skills": skills_data["soft_skills"]
    }


async def process_jd_file_upload(file: UploadFile, user_id: str) -> dict:
    """Processes JD file upload (.pdf, .docx, .txt), parses fields, stores in DB."""
    allowed_extensions = {".pdf", ".docx", ".txt"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Supported formats are PDF, DOCX, and TXT."
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    clean_filename = f"{user_id}_jd_{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, clean_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")
        
    # Check file size (<10MB)
    if os.path.getsize(file_path) > 10 * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    # Extract text based on file format
    if file_ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        text = extract_text_from_docx(file_path)
    else: # .txt
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read TXT file: {e}")

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="The uploaded file contains no readable text.")

    try:
        extracted_data = parse_job_description_complete(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse job description: {e}")

    jd_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "jd_name": file.filename,
        "jd_text": text,
        "original_file": file_path,
        "extracted_data": extracted_data,
        "upload_date": datetime.utcnow()
    }
    
    saved_doc = await create_job_description(jd_doc)
    return saved_doc


async def process_jd_text_upload(text: str, title: Optional[str], user_id: str) -> dict:
    """Processes raw pasted JD text, parses fields, stores in DB."""
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")

    try:
        extracted_data = parse_job_description_complete(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse job description: {e}")

    jd_name = title.strip() if title and title.strip() else (extracted_data.get("job_title") or "Pasted Job Description")

    jd_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "jd_name": jd_name,
        "jd_text": text,
        "original_file": None,
        "extracted_data": extracted_data,
        "upload_date": datetime.utcnow()
    }
    
    saved_doc = await create_job_description(jd_doc)
    return saved_doc


async def get_latest_jd(user_id: str) -> Optional[dict]:
    """Fetches the user's most recent job description."""
    return await get_latest_job_description(user_id)


async def get_jd_history(user_id: str) -> List[dict]:
    """Fetches list of all job descriptions uploaded by the user."""
    return await get_job_descriptions_by_user(user_id)


async def delete_jd(jd_id: str, user_id: str) -> bool:
    """Deletes a job description and cleans up associated file if present."""
    jd_doc = await get_job_description_by_id(jd_id, user_id)
    if not jd_doc:
        raise HTTPException(status_code=404, detail="Job description not found")
        
    deleted = await delete_job_description_by_id(jd_id, user_id)
    if deleted:
        original_file = jd_doc.get("original_file")
        if original_file and os.path.exists(original_file):
            try:
                os.remove(original_file)
            except Exception:
                pass
        return True
    return False
