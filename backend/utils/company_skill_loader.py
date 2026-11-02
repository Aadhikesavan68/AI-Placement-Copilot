from database.mongo import get_database
from utils.skill_extractor import normalize_skills
from datetime import datetime
import asyncio

COMPANY_PROFILES = [
    {
        "company_name": "Amazon",
        "skills": ["Java", "C++", "Python", "AWS", "SQL", "NoSQL", "Data Structures", "Algorithms", "System Design"],
        "preferred_skills": ["DynamoDB", "Spring Boot", "Microservices", "React", "Node.js"],
        "important_topics": ["Trees", "Graphs", "Dynamic Programming", "System Design"]
    },
    {
        "company_name": "Google",
        "skills": ["C++", "Java", "Python", "Go", "Data Structures", "Algorithms", "System Design"],
        "preferred_skills": ["GCP", "Kubernetes", "Machine Learning", "Distributed Systems", "Angular"],
        "important_topics": ["Graphs", "Dynamic Programming", "Trees", "System Design", "Arrays"]
    },
    {
        "company_name": "Microsoft",
        "skills": ["C#", "C++", "Java", "Python", "SQL", "Data Structures", "Algorithms", "System Design"],
        "preferred_skills": ["Azure", ".NET", "React", "TypeScript", "SQL Server"],
        "important_topics": ["Strings", "Linked List", "Trees", "System Design"]
    },
    {
        "company_name": "Meta",
        "skills": ["C++", "Java", "Python", "PHP", "JavaScript", "React", "Data Structures", "Algorithms"],
        "preferred_skills": ["GraphQL", "React Native", "MySQL", "Memcached", "System Design"],
        "important_topics": ["Arrays", "Strings", "Trees", "Graphs", "System Design"]
    },
    {
        "company_name": "Apple",
        "skills": ["Swift", "Objective-C", "C++", "Python", "Java", "Data Structures", "Algorithms"],
        "preferred_skills": ["iOS", "macOS", "Core Data", "Machine Learning", "System Design"],
        "important_topics": ["Arrays", "Strings", "Linked List", "Trees"]
    },
    {
        "company_name": "Netflix",
        "skills": ["Java", "Python", "JavaScript", "Node.js", "React", "AWS", "System Design"],
        "preferred_skills": ["Spring Boot", "Microservices", "Kafka", "Cassandra", "RxJava"],
        "important_topics": ["System Design", "Arrays", "Strings", "Dynamic Programming"]
    },
    {
        "company_name": "Uber",
        "skills": ["Go", "Java", "Python", "Node.js", "System Design", "Data Structures", "Algorithms"],
        "preferred_skills": ["Kafka", "Cassandra", "Redis", "Microservices", "React"],
        "important_topics": ["Graphs", "Trees", "Dynamic Programming", "System Design"]
    },
    {
        "company_name": "Adobe",
        "skills": ["C++", "Java", "Python", "JavaScript", "Data Structures", "Algorithms"],
        "preferred_skills": ["React", "Node.js", "AWS", "Machine Learning", "Computer Graphics"],
        "important_topics": ["Strings", "Arrays", "Linked List", "Trees"]
    },
    {
        "company_name": "Oracle",
        "skills": ["Java", "C++", "SQL", "PL/SQL", "Data Structures", "Algorithms"],
        "preferred_skills": ["Oracle DB", "Spring Boot", "Cloud Infrastructure", "Linux", "Python"],
        "important_topics": ["SQL", "DBMS", "Trees", "Linked List"]
    },
    {
        "company_name": "Cisco",
        "skills": ["C", "C++", "Python", "Java", "Networking", "Data Structures"],
        "preferred_skills": ["TCP/IP", "Linux", "Network Security", "AWS", "Go"],
        "important_topics": ["Computer Networks", "Arrays", "Strings", "Trees"]
    },
    {
        "company_name": "Salesforce",
        "skills": ["Java", "Apex", "JavaScript", "Python", "SQL", "Data Structures", "Algorithms"],
        "preferred_skills": ["Spring", "React", "AWS", "LWC", "System Design"],
        "important_topics": ["Strings", "Arrays", "Linked List", "System Design"]
    },
    {
        "company_name": "Atlassian",
        "skills": ["Java", "Python", "JavaScript", "React", "Data Structures", "Algorithms"],
        "preferred_skills": ["Spring Boot", "Node.js", "AWS", "Microservices", "System Design"],
        "important_topics": ["Arrays", "Strings", "Trees", "System Design"]
    },
    {
        "company_name": "TCS",
        "skills": ["Java", "Python", "SQL", "HTML", "CSS", "JavaScript"],
        "preferred_skills": ["Spring Boot", "Angular", "React", "AWS", "Azure", "DBMS"],
        "important_topics": ["Arrays", "Strings", "SQL", "DBMS", "OOP"]
    },
    {
        "company_name": "Infosys",
        "skills": ["Java", "Python", "SQL", "C++", "HTML", "JavaScript"],
        "preferred_skills": ["Spring Boot", "React", "Angular", "Cloud Computing", "DBMS"],
        "important_topics": ["Arrays", "Strings", "SQL", "OOP", "DBMS"]
    },
    {
        "company_name": "Wipro",
        "skills": ["Java", "Python", "C++", "SQL", "JavaScript"],
        "preferred_skills": ["Spring Boot", "React", "AWS", "Azure", "Machine Learning"],
        "important_topics": ["Arrays", "Strings", "SQL", "OOP"]
    },
    {
        "company_name": "Capgemini",
        "skills": ["Java", "Python", "SQL", "C#", "JavaScript"],
        "preferred_skills": ["Spring Boot", ".NET", "React", "AWS", "Azure"],
        "important_topics": ["Arrays", "Strings", "SQL", "DBMS", "OOP"]
    },
    {
        "company_name": "Cognizant",
        "skills": ["Java", "Python", "SQL", "C#", "JavaScript"],
        "preferred_skills": ["Spring Boot", "Angular", "React", "Cloud", "Testing"],
        "important_topics": ["Arrays", "Strings", "SQL", "OOP"]
    },
    {
        "company_name": "Zoho",
        "skills": ["Java", "C", "C++", "SQL", "JavaScript", "HTML", "CSS"],
        "preferred_skills": ["Spring", "React", "Ember.js", "MySQL", "PostgreSQL"],
        "important_topics": ["Arrays", "Strings", "Linked List", "DBMS", "OOP"]
    },
    {
        "company_name": "Freshworks",
        "skills": ["Ruby", "Java", "Python", "JavaScript", "SQL", "Data Structures"],
        "preferred_skills": ["Ruby on Rails", "Ember.js", "React", "AWS", "Redis"],
        "important_topics": ["Arrays", "Strings", "Trees", "System Design"]
    }
]

async def seed_company_skills():
    db = get_database()
    collection = db["company_skills"]
    
    count = await collection.count_documents({})
    if count > 0:
        return # Already seeded
        
    normalized_profiles = []
    for profile in COMPANY_PROFILES:
        normalized_profiles.append({
            "company_name": profile["company_name"],
            "skills": normalize_skills(profile["skills"]),
            "preferred_skills": normalize_skills(profile["preferred_skills"]),
            "important_topics": profile["important_topics"],
            "last_updated": datetime.utcnow()
        })
        
    await collection.insert_many(normalized_profiles)
    print(f"Seeded {len(normalized_profiles)} company skill profiles.")

async def get_company_profile(company_name: str) -> dict:
    db = get_database()
    profile = await db["company_skills"].find_one({"company_name": {"$regex": f"^{company_name}$", "$options": "i"}})
    if profile:
        profile["id"] = str(profile["_id"])
        del profile["_id"]
    return profile
