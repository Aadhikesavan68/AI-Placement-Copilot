import re
from utils.skill_extractor import normalize_skills

# A comprehensive list of tech keywords to look for in a JD
TECH_KEYWORDS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "ruby", "go", "golang", "swift", "kotlin",
    "php", "rust", "scala", "perl", "r", "matlab", "bash", "shell",
    "react", "angular", "vue", "node.js", "nodejs", "express", "django", "flask", "spring", "spring boot",
    "asp.net", "laravel", "ruby on rails", "fastapi", "next.js", "nuxt", "svelte",
    "mysql", "postgresql", "postgres", "mongodb", "sqlite", "oracle", "sql server", "redis", "cassandra",
    "elasticsearch", "dynamodb", "couchbase", "neo4j", "mariadb", "sql", "nosql",
    "aws", "amazon web services", "gcp", "google cloud", "azure", "heroku", "digitalocean",
    "docker", "kubernetes", "jenkins", "gitlab ci", "github actions", "travis ci", "circleci", "ansible",
    "terraform", "puppet", "chef", "vagran", "git", "github", "gitlab", "bitbucket",
    "machine learning", "deep learning", "artificial intelligence", "ai", "ml", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "hadoop", "spark", "kafka", "airflow", "tableau", "power bi", "snowflake", "databricks",
    "agile", "scrum", "kanban", "jira", "confluence", "trello", "asana",
    "linux", "unix", "windows", "macos", "ubuntu", "centos", "debian", "red hat",
    "rest", "graphql", "soap", "grpc", "websocket", "microservices", "serverless",
    "html", "css", "sass", "less", "tailwind", "bootstrap", "material ui", "chakra ui",
    "cypress", "jest", "mocha", "chai", "selenium", "puppeteer", "playwright", "junit", "pytest"
]

def extract_skills_from_jd(jd_text: str) -> list:
    """Extracts tech skills from a raw Job Description text."""
    if not jd_text:
        return []
        
    extracted = []
    text_lower = jd_text.lower()
    
    # Simple tokenization by word boundaries to match multi-word and single-word keywords
    for keyword in TECH_KEYWORDS:
        # Use regex to match whole words/phrases to avoid partial matches (e.g. 'c' in 'action')
        # \b doesn't work well with C++ or C#, so we handle special characters carefully.
        escaped_keyword = re.escape(keyword)
        # Check if keyword is surrounded by non-alphanumeric characters or start/end of string
        pattern = r'(^|[^a-z0-9])' + escaped_keyword + r'([^a-z0-9]|$)'
        
        if re.search(pattern, text_lower):
            extracted.append(keyword)
            
    return normalize_skills(extracted)
