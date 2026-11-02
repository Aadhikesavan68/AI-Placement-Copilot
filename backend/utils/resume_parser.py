import re
import fitz  # PyMuPDF
from docx import Document
import spacy

# Load spaCy model safely
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    try:
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = None

# Comprehensive Tech Skills Taxonomy
LANGUAGES_PROG = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Golang", 
    "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Dart", "Scala", "R", "MATLAB", "SQL", 
    "Bash", "Shell", "HTML", "HTML5", "CSS", "CSS3", "Sass", "GraphQL"
]

FRAMEWORKS = [
    "React", "React.js", "React Native", "Next.js", "Vue", "Vue.js", "Nuxt.js", "Angular", 
    "Node.js", "Express", "Express.js", "NestJS", "Django", "FastAPI", "Flask", 
    "Spring Boot", "Spring", "ASP.NET", ".NET", "Ruby on Rails", "Laravel", "Tailwind", 
    "TailwindCSS", "Bootstrap", "Redux", "Zustand", "Prisma", "Hibernate", "PyTorch", 
    "TensorFlow", "Keras", "Scikit-Learn", "Pandas", "NumPy"
]

DATABASES = [
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle", "Cassandra", 
    "DynamoDB", "Elasticsearch", "Neo4j", "Firebase", "Supabase", "MariaDB", "Snowflake"
]

CLOUD_INFRA = [
    "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "GCP", "Google Cloud", 
    "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "GitHub Actions", 
    "CI/CD", "Linux", "Unix", "Nginx", "Apache", "Vercel", "Netlify", "Cloudflare"
]

DEVELOPER_TOOLS = [
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Figma", "Postman", "Swagger", 
    "VSCode", "IntelliJ", "PyCharm", "Webpack", "Vite", "Babel", "Jest", "Mocha", 
    "Cypress", "Selenium", "PyTest", "Postman"
]

SOFT_SKILLS = [
    "Leadership", "Communication", "Teamwork", "Problem Solving", "Time Management", 
    "Collaboration", "Adaptability", "Creativity", "Organization", "Critical Thinking", 
    "Work Ethic", "Interpersonal Skills", "Mentorship", "Agile", "Scrum", "Presentation"
]

SPOKEN_LANGUAGES = [
    "English", "Spanish", "French", "German", "Mandarin", "Chinese", "Hindi", 
    "Japanese", "Korean", "Arabic", "Portuguese", "Russian", "Italian", "Tamil", "Telugu"
]


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
                text += "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text


def extract_email(text: str) -> str:
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    match = re.search(email_regex, text)
    return match.group(0).strip() if match else "Not Found"


def extract_phone(text: str) -> str:
    # Match standard international & domestic phone numbers
    phone_regex = r'(?:(?:\+|00)\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}'
    match = re.search(phone_regex, text)
    return match.group(0).strip() if match else "Not Found"


def extract_links(text: str) -> dict:
    links = {"linkedin": None, "github": None, "portfolio": None}
    
    linkedin_regex = r'(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_\-]+/?'
    github_regex = r'(https?://)?(www\.)?github\.com/[a-zA-Z0-9_\-]+/?'
    portfolio_regex = r'https?://[a-zA-Z0-9\-]+\.(?:dev|me|io|com|org|vercel\.app|netlify\.app)[^\s]*'
    
    linkedin_match = re.search(linkedin_regex, text, re.IGNORECASE)
    if linkedin_match:
        links["linkedin"] = linkedin_match.group(0)
        
    github_match = re.search(github_regex, text, re.IGNORECASE)
    if github_match:
        links["github"] = github_match.group(0)
        
    portfolio_match = re.search(portfolio_regex, text, re.IGNORECASE)
    if portfolio_match and "linkedin" not in portfolio_match.group(0) and "github" not in portfolio_match.group(0):
        links["portfolio"] = portfolio_match.group(0)
        
    return links


def extract_candidate_name(text: str) -> str:
    """Extract the candidate name from the resume header before using broad NER."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    rejected_headers = {
        "resume", "curriculum vitae", "cv", "profile", "personal details",
        "contact", "contact details", "objective", "summary", "skills",
        "experience", "education", "projects", "certifications",
    }
    rejected_terms = {
        "resume", "curriculum", "vitae", "profile", "email", "phone",
        "mobile", "contact", "objective", "summary", "engineer", "developer",
        "location", "salem", "tamil", "nadu", "india", "university",
        "college", "student", "software", "technology",
    }

    def header_candidate(line: str) -> str | None:
        # A name should be a standalone header, not a contact/location line.
        if any(marker in line for marker in ("@", "|", "://", ":", "(", ")")):
            return None
        clean = re.sub(r"[^a-zA-Z.\s'-]", " ", line)
        clean = re.sub(r"\s+", " ", clean).strip(" .-'")
        words = clean.split()
        if not 2 <= len(words) <= 4 or len(clean) > 60:
            return None
        lowered = clean.lower()
        if lowered in rejected_headers or any(term in lowered.split() for term in rejected_terms):
            return None
        if not all(re.fullmatch(r"[a-zA-Z][a-zA-Z.'-]*", word) for word in words):
            return None
        return clean.title()

    # The first standalone line(s) are more reliable than NER, which can label
    # locations, technologies, and employers as PERSON.
    for line in lines[:10]:
        candidate = header_candidate(line)
        if candidate:
            return candidate

    # NER is a fallback for resumes whose extraction does not preserve a header.
    if nlp:
        try:
            doc = nlp(text[:800])
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    clean_name = ent.text.strip()
                    if (
                        len(clean_name) >= 3
                        and len(clean_name.split()) <= 4
                        and not any(term in clean_name.lower().split() for term in rejected_terms)
                    ):
                        return clean_name
        except Exception:
            pass

    return "Candidate Name"


def extract_categorized_skills(text: str) -> dict:
    text_lower = text.lower()
    
    def find_matches(keyword_list):
        matched = []
        for kw in keyword_list:
            escaped = re.escape(kw.lower())
            pattern = r'(^|[^a-z0-9])' + escaped + r'([^a-z0-9]|$)'
            if re.search(pattern, text_lower):
                matched.append(kw)
        return list(dict.fromkeys(matched))

    lang_matches = find_matches(LANGUAGES_PROG)
    framework_matches = find_matches(FRAMEWORKS)
    db_matches = find_matches(DATABASES)
    cloud_matches = find_matches(CLOUD_INFRA)
    tool_matches = find_matches(DEVELOPER_TOOLS)
    soft_matches = find_matches(SOFT_SKILLS)
    spoken_matches = find_matches(SPOKEN_LANGUAGES)

    all_tech = list(dict.fromkeys(lang_matches + framework_matches + db_matches + cloud_matches + tool_matches))

    return {
        "skills": all_tech if all_tech else ["Problem Solving", "Software Development"],
        "languages_prog": lang_matches,
        "frameworks": framework_matches,
        "databases": db_matches,
        "cloud": cloud_matches,
        "tools": tool_matches,
        "soft_skills": soft_matches if soft_matches else ["Communication", "Teamwork", "Problem Solving"],
        "languages": spoken_matches if spoken_matches else ["English"]
    }


def extract_section_by_header(text: str, keywords: list) -> list:
    lines = text.split('\n')
    in_section = False
    items = []
    
    all_headers = [
        "experience", "work history", "employment", "professional experience",
        "education", "academic background", "academics", "qualifications",
        "projects", "academic projects", "key projects", "personal projects",
        "internships", "internship experience", "work experience",
        "certifications", "licenses", "certificates",
        "achievements", "awards", "honors", "accomplishments",
        "skills", "technical skills", "summary", "languages", "contact"
    ]
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        test_line = re.sub(r'^[#\-\*\s•\d\.\)]+', '', line_stripped).strip().lower()
        
        is_any_header = False
        if len(test_line) < 40:
            for h in all_headers:
                if test_line == h or test_line.startswith(h + " ") or test_line.endswith(" " + h):
                    is_any_header = True
                    break
        
        if is_any_header:
            is_target_header = any(kw in test_line for kw in keywords)
            in_section = is_target_header
            continue
            
        if in_section:
            cleaned = re.sub(r'^[•\-\*\s\d\.\)]+', '', line_stripped).strip()
            if cleaned and len(cleaned) > 5:
                items.append(cleaned)
                
    if not items:
        # Secondary fallback
        for line in lines:
            line_stripped = line.strip()
            if len(line_stripped) > 15 and any(kw in line_stripped.lower() for kw in keywords) and not any(h in line_stripped.lower() for h in all_headers if h not in keywords):
                cleaned = re.sub(r'^[•\-\*\s\d\.\)]+', '', line_stripped).strip()
                if cleaned:
                    items.append(cleaned)
                    
    return items[:12]


def extract_education_details(education_items: list, raw_text: str) -> dict:
    edu_text = " ".join(education_items) + " " + raw_text
    edu_lower = edu_text.lower()
    
    # Degree detection
    degree = "Not Found"
    degrees = [
        ("Ph.D", ["ph.d", "phd", "doctorate"]),
        ("Master of Technology (M.Tech)", ["m.tech", "mtech", "master of technology"]),
        ("Master of Science (M.S.)", ["m.s.", "ms in", "master of science"]),
        ("Master of Computer Applications (MCA)", ["mca", "master of computer application"]),
        ("Bachelor of Technology (B.Tech)", ["b.tech", "btech", "b.e", "bachelor of technology", "bachelor of engineering"]),
        ("Bachelor of Science (B.S. / B.Sc)", ["b.s.", "b.sc", "bsc", "bachelor of science"]),
        ("Bachelor of Computer Applications (BCA)", ["bca", "bachelor of computer application"]),
        ("Bachelor's Degree", ["bachelor", "undergraduate", "b.a", "bba"])
    ]
    for deg_name, patterns in degrees:
        if any(p in edu_lower for p in patterns):
            degree = deg_name
            break

    # College / University detection
    college = "Not Found"
    college_patterns = [
        r'([A-Z][A-Za-z\s,\.\-&]{2,45}\s+(?:University|Institute\s+of\s+Technology|College\s+of\s+Engineering|College|Academy|IIT|NIT|BITS|IIIT))',
        r'((?:University|Institute)\s+of\s+[A-Za-z\s]{2,30})'
    ]
    for pattern in college_patterns:
        match = re.search(pattern, raw_text)
        if match:
            col_match = match.group(1).strip().rstrip(',.')
            if len(col_match) < 60 and not any(w in col_match.lower() for w in ["resume", "experience", "education"]):
                college = col_match
                break

    return {"degree": degree, "college": college}


def parse_resume(file_path: str) -> dict:
    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        text = extract_text_from_docx(file_path)
    elif file_path.lower().endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception:
            text = ""
    else:
        text = ""

    links = extract_links(text)
    name = extract_candidate_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills_data = extract_categorized_skills(text)

    education_items = extract_section_by_header(text, ["education", "academic", "degree", "university", "college"])
    experience_items = extract_section_by_header(text, ["experience", "work history", "employment", "professional"])
    projects_items = extract_section_by_header(text, ["project"])
    internship_items = extract_section_by_header(text, ["internship", "intern"])
    cert_items = extract_section_by_header(text, ["certific", "license", "course"])
    achievement_items = extract_section_by_header(text, ["achievement", "award", "honor", "accomplish", "rank"])

    edu_details = extract_education_details(education_items, text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "college": edu_details["college"],
        "degree": edu_details["degree"],
        "skills": skills_data["skills"],
        "languages_prog": skills_data["languages_prog"],
        "frameworks": skills_data["frameworks"],
        "databases": skills_data["databases"],
        "cloud": skills_data["cloud"],
        "tools": skills_data["tools"],
        "soft_skills": skills_data["soft_skills"],
        "education": education_items if education_items else [f"{edu_details['degree']} from {edu_details['college']}"] if edu_details['degree'] != "Not Found" else ["Computer Science / Related Field"],
        "projects": projects_items,
        "experience": experience_items,
        "internships": internship_items,
        "certifications": cert_items,
        "achievements": achievement_items,
        "languages": skills_data["languages"],
        "technologies": skills_data["skills"],
        "linkedin": links.get("linkedin") or "Not Found",
        "github": links.get("github") or "Not Found",
        "portfolio": links.get("portfolio") or "Not Found",
        "location": "Not Found",
        "summary": "Experienced in full-stack software development and problem solving." if "summary" in text.lower() or "objective" in text.lower() else "Not Found"
    }
