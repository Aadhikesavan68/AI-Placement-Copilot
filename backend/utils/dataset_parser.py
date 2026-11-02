import csv
import os
import random

# Predefined topics to infer from titles (basic mapping)
TOPIC_MAPPING = {
    "array": "Arrays",
    "string": "Strings",
    "list": "Linked List",
    "tree": "Trees",
    "graph": "Graphs",
    "sum": "Arrays", # e.g. Two Sum
    "search": "Algorithms",
    "sort": "Algorithms",
    "dynamic": "Dynamic Programming",
    "dp": "Dynamic Programming",
    "greedy": "Greedy",
    "sql": "SQL",
    "database": "DBMS"
}

def infer_topic(title: str) -> str:
    title_lower = title.lower()
    for keyword, topic in TOPIC_MAPPING.items():
        if keyword in title_lower:
            return topic
    # Default topic if nothing matches
    return random.choice(["Arrays", "Strings", "Trees", "Dynamic Programming", "Graphs"])

def parse_company_csv(filepath: str, company_name: str) -> list:
    questions = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row.get("Title", "").strip()
                if not title:
                    continue
                
                difficulty = row.get("Difficulty", "Medium")
                url = row.get("URL", "")
                
                topic = infer_topic(title)
                
                question = {
                    "company": company_name,
                    "title": title,
                    "difficulty": difficulty,
                    "topic": topic,
                    "leetcode_link": url,
                    "tags": [topic, difficulty]
                }
                questions.append(question)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return questions
