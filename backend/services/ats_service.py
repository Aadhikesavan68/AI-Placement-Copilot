import re
import math
from typing import Dict, List, Any
from schemas.roadmap_schema import RoadmapWeek, CourseRecommendation
from schemas.ats_schema import CategorizedMissingSkill, InterviewQuestion
from utils.skill_extractor import normalize_skills, normalize_skill

ALL_TOOLS = [
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello", "asana", 
    "slack", "figma", "docker", "kubernetes", "jenkins", "terraform", "ansible", 
    "postman", "vscode", "intellij", "linux", "vite", "webpack", "ci/cd"
]

ALL_SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "time management", 
    "collaboration", "adaptability", "creativity", "organization", "work ethic", 
    "interpersonal", "critical thinking", "mentorship", "agile", "scrum"
]

# Comprehensive resource dictionary for all skills
LEARNING_RESOURCES_MAP = {
    "react": {"name": "React - The Complete Guide (Hooks, React Router, Redux)", "provider": "Udemy", "hours": "40 hours", "diff": "Intermediate", "url": "https://react.dev/learn"},
    "next.js": {"name": "Mastering Next.js & App Router", "provider": "Next.js Learn", "hours": "25 hours", "diff": "Intermediate", "url": "https://nextjs.org/learn"},
    "node.js": {"name": "Node.js Developer Course (REST APIs, Microservices)", "provider": "Coursera", "hours": "30 hours", "diff": "Intermediate", "url": "https://nodejs.org/en/docs"},
    "python": {"name": "Complete Python Developer Bootcamp", "provider": "Udemy", "hours": "25 hours", "diff": "Beginner", "url": "https://docs.python.org/3/tutorial/"},
    "fastapi": {"name": "FastAPI Masterclass - Modern High-Performance APIs", "provider": "freeCodeCamp", "hours": "15 hours", "diff": "Intermediate", "url": "https://fastapi.tiangolo.com/tutorial/"},
    "django": {"name": "Django for Beginners & Production APIs", "provider": "Coursera", "hours": "30 hours", "diff": "Intermediate", "url": "https://docs.djangoproject.com/"},
    "java": {"name": "Java Programming Masterclass", "provider": "Udemy", "hours": "45 hours", "diff": "Intermediate", "url": "https://dev.java/learn/"},
    "spring boot": {"name": "Spring Boot 3 & Microservices Deep Dive", "provider": "Baeldung", "hours": "35 hours", "diff": "Advanced", "url": "https://spring.io/guides"},
    "typescript": {"name": "Understanding TypeScript - 2026 Edition", "provider": "Udemy", "hours": "20 hours", "diff": "Beginner", "url": "https://www.typescriptlang.org/docs/"},
    "javascript": {"name": "The Complete JavaScript Course", "provider": "Udemy", "hours": "35 hours", "diff": "Beginner", "url": "https://javascript.info/"},
    "docker": {"name": "Docker & Kubernetes: The Practical Guide", "provider": "Udemy", "hours": "22 hours", "diff": "Intermediate", "url": "https://docs.docker.com/get-started/"},
    "kubernetes": {"name": "Kubernetes Mastery: Hands-On Cluster Architecture", "provider": "Cloud Native Academy", "hours": "30 hours", "diff": "Advanced", "url": "https://kubernetes.io/docs/tutorials/"},
    "aws": {"name": "AWS Certified Solutions Architect Associate", "provider": "Coursera", "hours": "35 hours", "diff": "Intermediate", "url": "https://aws.amazon.com/training/"},
    "postgresql": {"name": "PostgreSQL Bootcamp: High Performance Queries", "provider": "Udemy", "hours": "18 hours", "diff": "Intermediate", "url": "https://www.postgresqltutorial.com/"},
    "mongodb": {"name": "MongoDB - The Complete Developer Guide", "provider": "MongoDB University", "hours": "15 hours", "diff": "Intermediate", "url": "https://learn.mongodb.com/"},
    "redis": {"name": "Redis In-Memory Caching & Architecture", "provider": "Redis University", "hours": "10 hours", "diff": "Intermediate", "url": "https://university.redis.com/"},
    "graphql": {"name": "GraphQL with Node.js & React", "provider": "Apollo Odyssey", "hours": "15 hours", "diff": "Intermediate", "url": "https://graphql.org/learn/"},
    "ci/cd": {"name": "GitHub Actions & DevOps CI/CD Pipelines", "provider": "freeCodeCamp", "hours": "12 hours", "diff": "Intermediate", "url": "https://docs.github.com/en/actions"},
    "system design": {"name": "System Design Interview Prep & Scalability", "provider": "Educative.io", "hours": "25 hours", "diff": "Advanced", "url": "https://github.com/donnemartin/system-design-primer"},
    "data structures": {"name": "Data Structures & Algorithms in Practice", "provider": "LeetCode / NeetCode", "hours": "40 hours", "diff": "Intermediate", "url": "https://neetcode.io/"}
}


def parse_job_description_text(jd_text: str) -> dict:
    """Deterministic JD parsing to extract key ATS comparison metrics."""
    if not jd_text:
        return {}
        
    text_lower = jd_text.lower()
    
    # 1. Company Name Extraction Heuristic
    company_name = "Target Company"
    company_patterns = [
        r'(?:about|at)\s+([A-Z][a-zA-Z0-9\s\.\,\-\&]{1,30})(?:\s+is\s+a|\s+believes|\s+focuses)',
        r'company:\s*([A-Za-z0-9\s\.\,\-\&]{1,30})',
        r'welcome\s+to\s+([A-Z][a-zA-Z0-9\s\.\,\-\&]{1,30})'
    ]
    for pattern in company_patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip().rstrip('.,;')
            break
            
    # 2. Role Title Extraction
    role = "Software Engineer"
    role_patterns = [
        r'(?:title|role|position)\s*[:\-–]\s*([A-Za-z0-9\s\.\#\-\+\&\/\(\)]{3,50})',
        r'(?:hiring|looking\s+for)\s+(?:a|an)?\s*([A-Za-z0-9\s\.\#\-\+\&\/\(\)]{3,50})'
    ]
    for pattern in role_patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            role = match.group(1).strip()
            break
    else:
        first_lines = [l.strip() for l in jd_text.split('\n')[:4] if l.strip()]
        role_indicators = ["engineer", "developer", "architect", "manager", "analyst", "lead", "specialist"]
        for line in first_lines:
            if any(ind in line.lower() for ind in role_indicators) and len(line) < 60:
                role = re.sub(r'^[#\*\-\•\s]+', '', line).strip()
                break

    # 3. Extract skills and technologies
    from utils.jd_parser import TECH_KEYWORDS
    extracted_skills = []
    for keyword in TECH_KEYWORDS:
        escaped_keyword = re.escape(keyword)
        pattern = r'(^|[^a-z0-9])' + escaped_keyword + r'([^a-z0-9]|$)'
        if re.search(pattern, text_lower):
            extracted_skills.append(keyword)
            
    skills = normalize_skills(extracted_skills)
    
    # Split skills into required and preferred based on sections
    required_skills = []
    preferred_skills = []
    
    lines = jd_text.split('\n')
    in_preferred_section = False
    for line in lines:
        line_clean = line.strip().lower()
        if any(p in line_clean for p in ["preferred", "nice to have", "plus", "bonus", "desirable"]):
            in_preferred_section = True
        elif any(r in line_clean for r in ["required", "minimum", "basic qualification", "must have", "requirements"]):
            in_preferred_section = False
            
        line_skills = [s for s in skills if re.search(r'\b' + re.escape(s.lower()) + r'\b', line_clean)]
        for s in line_skills:
            if in_preferred_section:
                if s not in preferred_skills: preferred_skills.append(s)
            else:
                if s not in required_skills: required_skills.append(s)
                
    if not required_skills:
        required_skills = skills
        
    # 4. Experience Heuristic
    required_experience = "0-2 years"
    exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:work|professional)?\s*experience', text_lower)
    if exp_match:
        required_experience = f"{exp_match.group(1)}+ years"

    # 5. Education Heuristic
    education = []
    edu_indicators = {
        "bachelor": "Bachelor's Degree in Computer Science or related field",
        "b.s": "Bachelor of Science (B.S.) in Computer Science",
        "b.tech": "Bachelor of Technology (B.Tech)",
        "master": "Master's Degree (M.S. / M.Tech)",
        "phd": "PhD / Doctorate in Computer Science",
    }
    for key, val in edu_indicators.items():
        if key in text_lower and val not in education:
            education.append(val)
    if not education:
        education = ["Bachelor's Degree in Computer Science, Engineering, or related technical field"]

    # 6. Responsibilities Section Heuristic
    responsibilities = []
    in_resp = False
    for line in lines:
        line_clean = line.strip()
        if not line_clean: continue
        
        is_header = len(line_clean) < 40 and any(h in line_clean.lower() for h in ["responsibilities", "what you'll do", "duties", "role", "key tasks"])
        if is_header:
            in_resp = True
            continue
        elif len(line_clean) < 40 and any(h in line_clean.lower() for h in ["requirements", "skills", "experience", "education", "preferred"]):
            in_resp = False
            
        if in_resp:
            bullet = re.sub(r'^[•\-\*\s\d\.\)]+', '', line_clean).strip()
            if bullet and len(bullet) > 10: responsibilities.append(bullet)
            
    if not responsibilities:
        for line in lines:
            line_clean = line.strip()
            if (line_clean.startswith('•') or line_clean.startswith('-') or line_clean.startswith('*')) and len(line_clean) > 20:
                bullet = re.sub(r'^[•\-\*\s]+', '', line_clean).strip()
                responsibilities.append(bullet)
                
    # 7. Tools and Soft Skills
    tools = [tool.title() for tool in ALL_TOOLS if re.search(r'\b' + re.escape(tool) + r'\b', text_lower)]
    soft_skills = [soft.title() for soft in ALL_SOFT_SKILLS if re.search(r'\b' + re.escape(soft) + r'\b', text_lower)]
    
    return {
        "company_name": company_name,
        "job_title": role,
        "role": role,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "required_experience": required_experience,
        "experience": required_experience,
        "education": education,
        "responsibilities": responsibilities[:10],
        "keywords": list(dict.fromkeys(skills + tools + soft_skills)),
        "tools": tools,
        "technologies": skills,
        "soft_skills": soft_skills
    }


def calculate_cosine_similarity(text1: str, text2: str) -> float:
    words1 = re.findall(r'\w+', text1.lower())
    words2 = re.findall(r'\w+', text2.lower())
    if not words1 or not words2:
        return 0.0
    vec1, vec2 = {}, {}
    for w in words1: vec1[w] = vec1.get(w, 0) + 1
    for w in words2: vec2[w] = vec2.get(w, 0) + 1
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator: return 0.0
    return min(100.0, (numerator / denominator) * 100)


def categorize_missing_skills(missing_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> List[CategorizedMissingSkill]:
    categorized = []
    for skill in missing_skills:
        skill_lower = skill.lower()
        res_info = LEARNING_RESOURCES_MAP.get(skill_lower, {
            "name": f"Mastering {skill} - Modern Guide & Projects",
            "provider": "freeCodeCamp / Official Docs",
            "hours": "15-20 hours",
            "diff": "Intermediate",
            "url": f"https://www.google.com/search?q={skill}+documentation+tutorial"
        })
        
        # Categorize
        if skill in required_skills or any(skill_lower in s.lower() for s in required_skills):
            category = "Critical"
            priority = "High"
        elif skill in preferred_skills or any(skill_lower in s.lower() for s in preferred_skills):
            category = "Optional"
            priority = "Low"
        else:
            category = "Important"
            priority = "Medium"
            
        categorized.append(CategorizedMissingSkill(
            skill=skill,
            category=category,
            difficulty=res_info["diff"],
            estimated_hours=res_info["hours"],
            priority=priority,
            resource_name=res_info["name"],
            resource_url=res_info["url"]
        ))
    return categorized


def generate_tailored_interview_questions(matched_skills: List[str], missing_skills: List[str], role: str) -> List[InterviewQuestion]:
    questions = []
    for skill in matched_skills[:3]:
        questions.append(InterviewQuestion(
            question=f"Can you describe a complex real-world project where you utilized {skill} and how you handled performance optimizations?",
            category="Technical Core",
            tip=f"Structure your answer using the STAR method (Situation, Task, Action, Result) highlighting your specific contributions with {skill}."
        ))
        
    for skill in missing_skills[:2]:
        questions.append(InterviewQuestion(
            question=f"This role frequently uses {skill}. How do you approach picking up new technologies rapidly under production deadlines?",
            category="Adaptability & Growth",
            tip="Demonstrate your learning process, previous quick-learning achievements, and enthusiasm for mastering the company stack."
        ))
        
    questions.append(InterviewQuestion(
        question="Tell me about a challenging technical trade-off you had to make between development speed and system scalability.",
        category="System Architecture",
        tip="Walk through the constraints, the options evaluated, why you made the decision, and how it impacted users and maintainability."
    ))
    return questions


def generate_structured_roadmap(missing_skills: List[str], target_role: str) -> List[dict]:
    roadmap = []
    
    # Week 1: Core Fundamentals & Primary Gaps
    w1_skills = missing_skills[:2] if missing_skills else ["Core CS Fundamentals", "Data Structures"]
    w1_resources = []
    for s in w1_skills:
        info = LEARNING_RESOURCES_MAP.get(s.lower(), {"name": f"Comprehensive {s} Guide", "provider": "freeCodeCamp", "diff": "Intermediate", "hours": "15h", "url": "https://roadmap.sh"})
        w1_resources.append(CourseRecommendation(course_name=info["name"], provider=info["provider"], difficulty=info["diff"], estimated_duration=info["hours"], url=info["url"]))
    roadmap.append(RoadmapWeek(
        week=1,
        topic=f"Foundations: {', '.join(w1_skills)}",
        description=f"Deep dive into syntax, core paradigms, and build hands-on code examples for {', '.join(w1_skills)}.",
        resources=w1_resources
    ).model_dump())
    
    # Week 2: Frameworks & System Integration
    w2_skills = missing_skills[2:4] if len(missing_skills) > 2 else ["REST APIs", "Database Optimization"]
    w2_resources = []
    for s in w2_skills:
        info = LEARNING_RESOURCES_MAP.get(s.lower(), {"name": f"Mastering {s} in Production", "provider": "Udemy", "diff": "Intermediate", "hours": "18h", "url": "https://roadmap.sh"})
        w2_resources.append(CourseRecommendation(course_name=info["name"], provider=info["provider"], difficulty=info["diff"], estimated_duration=info["hours"], url=info["url"]))
    roadmap.append(RoadmapWeek(
        week=2,
        topic=f"Frameworks & Architecture: {', '.join(w2_skills)}",
        description="Integrate backend services, design resilient schemas, and construct end-to-end API endpoints.",
        resources=w2_resources
    ).model_dump())
    
    # Week 3: Cloud, Tooling & Containerization
    w3_skills = missing_skills[4:6] if len(missing_skills) > 4 else ["Docker & CI/CD", "Cloud Architecture"]
    w3_resources = []
    for s in w3_skills:
        info = LEARNING_RESOURCES_MAP.get(s.lower(), {"name": f"DevOps & Deployment with {s}", "provider": "Coursera", "diff": "Advanced", "hours": "15h", "url": "https://roadmap.sh"})
        w3_resources.append(CourseRecommendation(course_name=info["name"], provider=info["provider"], difficulty=info["diff"], estimated_duration=info["hours"], url=info["url"]))
    roadmap.append(RoadmapWeek(
        week=3,
        topic=f"Cloud & Infrastructure: {', '.join(w3_skills)}",
        description="Containerize applications, configure automated CI/CD pipelines, and deploy on scalable cloud infrastructure.",
        resources=w3_resources
    ).model_dump())
    
    # Week 4: Capstone Portfolio Project & Mock Interview Prep
    roadmap.append(RoadmapWeek(
        week=4,
        topic=f"Capstone Project & {target_role} Interview Readiness",
        description="Build a production-grade full-stack project incorporating all learned skills and practice targeted behavioral & technical interview questions.",
        resources=[
            CourseRecommendation(course_name="System Design Primer & Interview Prep", provider="GitHub", difficulty="Advanced", estimated_duration="20h", url="https://github.com/donnemartin/system-design-primer"),
            CourseRecommendation(course_name="NeetCode 150 - Coding Interview Mastery", provider="NeetCode", difficulty="Intermediate", estimated_duration="25h", url="https://neetcode.io")
        ]
    ).model_dump())
    
    return roadmap


def compare_resume_and_jd(resume_data: dict, jd_data: dict, file_type: str = "pdf") -> dict:
    """Comprehensive ATS scoring & intelligent matching engine."""
    # 1. Extract and normalize skills
    req_skills = jd_data.get("required_skills", [])
    pref_skills = jd_data.get("preferred_skills", [])
    all_jd_skills = list(dict.fromkeys(req_skills + pref_skills + jd_data.get("technologies", [])))
    
    res_skills = resume_data.get("skills", [])
    res_skills_normalized = [s.lower() for s in res_skills]
    
    matched_skills = []
    missing_skills = []
    for s in all_jd_skills:
        if any(s.lower() == rs or s.lower() in rs or rs in s.lower() for rs in res_skills_normalized):
            matched_skills.append(s)
        else:
            missing_skills.append(s)
            
    extra_skills = [s for s in res_skills if not any(s.lower() == js.lower() or s.lower() in js.lower() for js in all_jd_skills)]

    # Sub-scores
    skill_match = int((len(matched_skills) / len(all_jd_skills) * 100)) if all_jd_skills else 95
    
    # 2. Experience Match Score
    req_exp = jd_data.get("required_experience", "0")
    req_years = 0
    num_match = re.search(r'(\d+)', req_exp)
    if num_match:
        req_years = int(num_match.group(1))
        
    resume_exp_items = resume_data.get("experience", [])
    res_years = max(1.0, len(resume_exp_items) * 1.5)
    exp_match = 100 if req_years == 0 else min(100, int((res_years / req_years) * 100))

    # 3. Education Match Score
    jd_edu = " ".join(jd_data.get("education", [])).lower()
    res_edu = " ".join(resume_data.get("education", [])).lower() + " " + str(resume_data.get("degree", "")).lower()
    education_match = 100 if any(d in res_edu for d in ["bachelor", "b.tech", "b.s", "master", "m.tech", "phd", "computer science", "engineering"]) else 70

    # 4. Keyword Match Score
    jd_keywords = jd_data.get("keywords", [])
    res_text = " ".join([
        resume_data.get("name", ""),
        " ".join(resume_data.get("skills", [])),
        " ".join(resume_data.get("projects", [])),
        " ".join(resume_data.get("experience", [])),
        " ".join(resume_data.get("certifications", [])),
        " ".join(resume_data.get("achievements", [])),
        resume_data.get("summary", "") or ""
    ]).lower()
    
    matched_keywords = [k for k in jd_keywords if re.search(r'\b' + re.escape(k.lower()) + r'\b', res_text)]
    missing_keywords = [k for k in jd_keywords if k not in matched_keywords]
    keyword_match = int((len(matched_keywords) / len(jd_keywords) * 100)) if jd_keywords else 90

    # 5. Semantic Match & Project Relevance
    jd_resp_text = " ".join(jd_data.get("responsibilities", []))
    res_proj_text = " ".join(resume_data.get("projects", []))
    res_exp_text = " ".join(resume_data.get("experience", []))
    
    responsibilities_match = int(calculate_cosine_similarity(res_exp_text, jd_resp_text))
    responsibilities_match = max(responsibilities_match, int(keyword_match * 0.7))
    
    project_relevance = int(calculate_cosine_similarity(res_proj_text, jd_resp_text))
    project_relevance = max(project_relevance, int(skill_match * 0.75))
    
    semantic_match = int((skill_match * 0.4) + (keyword_match * 0.3) + (responsibilities_match * 0.3))

    # Overall Match Score
    match_score = int(
        skill_match * 0.35 +
        exp_match * 0.20 +
        education_match * 0.10 +
        keyword_match * 0.15 +
        responsibilities_match * 0.10 +
        project_relevance * 0.10
    )
    match_score = max(25, min(99, match_score))

    # 6. 12-Factor ATS Details
    formatting = 100 if file_type in ["pdf", "docx"] else 75
    
    good_sections = []
    weak_sections = []
    missing_sections = []
    
    section_checks = {
        "experience": (resume_data.get("experience"), "Work Experience"),
        "education": (resume_data.get("education"), "Education"),
        "skills": (resume_data.get("skills"), "Skills"),
        "projects": (resume_data.get("projects"), "Projects"),
        "certifications": (resume_data.get("certifications"), "Certifications"),
        "achievements": (resume_data.get("achievements"), "Achievements / Awards")
    }
    for key, (val, name) in section_checks.items():
        if val and len(val) > 0 and val != ["Not Found"]:
            good_sections.append(name)
        elif val:
            weak_sections.append(name)
        else:
            missing_sections.append(name)
            
    section_presence = int((len(good_sections) / len(section_checks)) * 100)
    keyword_optimization = keyword_match
    
    total_words = len(res_text.split())
    readability = 95 if 350 <= total_words <= 1100 else 75
    
    has_email = resume_data.get("email") and resume_data.get("email") != "Not Found"
    has_phone = resume_data.get("phone") and resume_data.get("phone") != "Not Found"
    contact_information = 100 if (has_email and has_phone) else 65
    
    projects_score = min(100, max(40, len(resume_data.get("projects", [])) * 35))
    experience_score = min(100, max(40, len(resume_data.get("experience", [])) * 30))
    education_score = education_match
    achievements_score = 95 if resume_data.get("achievements") and len(resume_data.get("achievements", [])) > 0 else 50
    skills_score = min(100, max(40, len(res_skills) * 8))
    
    action_verbs = ["managed", "led", "developed", "designed", "implemented", "created", "built", "optimized", "architected", "delivered", "deployed", "scaled"]
    verb_count = sum(1 for verb in action_verbs if verb in res_text)
    action_verbs_score = min(100, max(30, verb_count * 18))
    
    resume_length = 95 if 400 <= total_words <= 1200 else 70
    consistency = 90

    ats_score = int(
        formatting * 0.05 +
        section_presence * 0.15 +
        keyword_optimization * 0.15 +
        readability * 0.10 +
        contact_information * 0.05 +
        projects_score * 0.10 +
        experience_score * 0.10 +
        education_score * 0.05 +
        achievements_score * 0.05 +
        skills_score * 0.10 +
        action_verbs_score * 0.10
    )
    ats_score = max(30, min(99, ats_score))

    # 7. Strengths, Weaknesses, Suggestions
    strengths = []
    if skill_match >= 70:
        strengths.append(f"Strong overlap with {len(matched_skills)} target skills required for this role.")
    if len(resume_data.get("projects", [])) >= 2:
        strengths.append(f"Demonstrated hands-on experience through {len(resume_data.get('projects', []))} technical projects.")
    if education_match >= 85:
        strengths.append("Educational background aligns directly with the qualification requirements.")
    if verb_count >= 4:
        strengths.append("Effective use of strong action verbs across professional bullet points.")
    if not strengths:
        strengths.append("Solid technical foundation ready for targeted interview preparation.")

    weaknesses = []
    if len(missing_skills) > 0:
        weaknesses.append(f"Missing key job requirements: {', '.join(missing_skills[:3])}.")
    if not resume_data.get("achievements") or len(resume_data.get("achievements", [])) == 0:
        weaknesses.append("Lack of quantifiable achievements or competition/awards section.")
    if verb_count < 3:
        weaknesses.append("Action verbs could be stronger in experience and project descriptions.")
    if total_words < 300:
        weaknesses.append("Resume content is too brief; expand project descriptions with metrics.")

    suggestions = []
    if missing_skills:
        suggestions.append(f"Incorporate relevant experience and project keywords for: {', '.join(missing_skills[:3])}.")
    suggestions.append("Add measurable metrics to all project bullets (e.g. 'Reduced latency by 35%', 'Served 10K+ monthly active users').")
    if verb_count < 4:
        suggestions.append("Start bullet points with impactful verbs like 'Architected', 'Engineered', 'Optimized', and 'Delivered'.")
    if contact_information < 90:
        suggestions.append("Ensure your complete email, phone number, and clickable LinkedIn/GitHub profiles are prominently visible at the top.")

    # 8. Missing Skills Categorization & Roadmap
    categorized_missing = categorize_missing_skills(missing_skills, req_skills, pref_skills)
    target_role = jd_data.get("role") or "Software Engineer"
    roadmap_weeks = generate_structured_roadmap(missing_skills, target_role)
    interview_qs = generate_tailored_interview_questions(matched_skills, missing_skills, target_role)

    # 9. Readiness Metrics
    interview_readiness = int((match_score * 0.5) + (ats_score * 0.3) + (action_verbs_score * 0.2))
    interview_readiness = max(35, min(95, interview_readiness))
    company_readiness = int((match_score * 0.6) + (semantic_match * 0.4))
    company_readiness = max(30, min(96, company_readiness))
    confidence_score = 92 if len(all_jd_skills) > 3 else 82

    ai_suggestions = [
        f"Your resume matches {match_score}% of the target requirements for {target_role} at {jd_data.get('company_name', 'Target Company')}.",
        f"Prioritize mastering {', '.join(missing_skills[:2]) if missing_skills else 'advanced cloud architecture'} to reach a 90%+ match score.",
        "Highlight full-stack deployment and CI/CD pipelines in your recent project summaries."
    ]

    return {
        "ats_score": ats_score,
        "match_score": match_score,
        "interview_readiness": interview_readiness,
        "company_readiness": company_readiness,
        "confidence_score": confidence_score,
        "semantic_match": semantic_match,
        "scores": {
            "skill_match": skill_match,
            "experience_match": exp_match,
            "education_match": education_match,
            "keyword_match": keyword_match,
            "responsibilities_match": responsibilities_match,
            "project_relevance": project_relevance,
            "semantic_match": semantic_match
        },
        "ats_details": {
            "formatting": formatting,
            "section_presence": section_presence,
            "keyword_optimization": keyword_optimization,
            "readability": readability,
            "contact_information": contact_information,
            "projects": projects_score,
            "experience": experience_score,
            "education": education_score,
            "achievements": achievements_score,
            "skills": skills_score,
            "action_verbs": action_verbs_score,
            "resume_length": resume_length,
            "consistency": consistency
        },
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "missing_skills_categorized": [s.model_dump() for s in categorized_missing],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "keywords": {
            "existing_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "recommended_keywords": list(dict.fromkeys(jd_keywords))
        },
        "ai_suggestions": ai_suggestions,
        "highlights": {
            "good_sections": good_sections,
            "weak_sections": weak_sections,
            "missing_sections": missing_sections
        },
        "interview_questions": [q.model_dump() for q in interview_qs],
        "roadmap": roadmap_weeks
    }
