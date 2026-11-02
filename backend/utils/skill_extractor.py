import re

# Dictionary to map varying skill names to a standard keyword
SKILL_MAP = {
    "c plus plus": "C++",
    "cpp": "C++",
    "c++": "C++",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "python": "Python",
    "python3": "Python",
    "java": "Java",
    "j2ee": "Java",
    "go": "Go",
    "golang": "Go",
    "c#": "C#",
    "csharp": "C#",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "nosql": "NoSQL",
    "git": "Git",
    "github": "Git",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "artificial intelligence": "AI",
    "ai": "AI"
}

def normalize_skill(skill: str) -> str:
    """Normalizes a skill string to standard format."""
    clean_skill = skill.lower().strip()
    if clean_skill in SKILL_MAP:
        return SKILL_MAP[clean_skill]
    
    # Capitalize appropriately if not in map
    if len(clean_skill) <= 3:
        return clean_skill.upper()
    return clean_skill.title()

def normalize_skills(skills: list) -> list:
    """Takes a list of skills, normalizes them, and removes duplicates."""
    normalized = []
    for skill in skills:
        if not skill:
            continue
        norm = normalize_skill(skill)
        if norm not in normalized:
            normalized.append(norm)
    return normalized
