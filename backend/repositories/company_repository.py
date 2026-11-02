from database.mongo import get_database
from typing import List, Optional
import re

async def get_all_companies():
    db = get_database()
    companies = []
    async for doc in db["companies"].find().sort("company_name", 1):
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        companies.append(doc)
    return companies

async def search_companies(query: str):
    db = get_database()
    companies = []
    # Case insensitive search on company_name
    regex = re.compile(query, re.IGNORECASE)
    async for doc in db["companies"].find({"company_name": regex}):
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        companies.append(doc)
    return companies

async def get_company_by_name(name: str):
    db = get_database()
    # Find exact match but case insensitive
    regex = re.compile(f"^{name}$", re.IGNORECASE)
    doc = await db["companies"].find_one({"company_name": regex})
    if doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

async def get_company_questions(company_name: str, skip: int = 0, limit: int = 20, difficulty: str = None, topic: str = None):
    db = get_database()
    query = {"company": re.compile(f"^{company_name}$", re.IGNORECASE)}
    if difficulty:
        query["difficulty"] = re.compile(f"^{difficulty}$", re.IGNORECASE)
    if topic:
        query["topic"] = re.compile(f"^{topic}$", re.IGNORECASE)
        
    questions = []
    cursor = db["technical_questions"].find(query).skip(skip).limit(limit)
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        questions.append(doc)
    
    total = await db["technical_questions"].count_documents(query)
    return {"questions": questions, "total": total}

async def get_company_topics(company_name: str):
    db = get_database()
    pipeline = [
        {"$match": {"company": re.compile(f"^{company_name}$", re.IGNORECASE)}},
        {"$group": {"_id": "$topic", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    topics = []
    async for doc in db["technical_questions"].aggregate(pipeline):
        if doc["_id"]: # Ignore null topics
            topics.append({"topic": doc["_id"], "count": doc["count"]})
    return topics

async def get_company_stats(company_name: str):
    db = get_database()
    pipeline = [
        {"$match": {"company": re.compile(f"^{company_name}$", re.IGNORECASE)}},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "easy": {"$sum": {"$cond": [{"$regexMatch": {"input": "$difficulty", "regex": "^easy$", "options": "i"}}, 1, 0]}},
            "medium": {"$sum": {"$cond": [{"$regexMatch": {"input": "$difficulty", "regex": "^medium$", "options": "i"}}, 1, 0]}},
            "hard": {"$sum": {"$cond": [{"$regexMatch": {"input": "$difficulty", "regex": "^hard$", "options": "i"}}, 1, 0]}}
        }}
    ]
    stats = await db["technical_questions"].aggregate(pipeline).to_list(1)
    if stats:
        return {
            "total_questions": stats[0]["total"],
            "easy": stats[0]["easy"],
            "medium": stats[0]["medium"],
            "hard": stats[0]["hard"]
        }
    return {"total_questions": 0, "easy": 0, "medium": 0, "hard": 0}

async def toggle_question_bookmark(question_id: str, user_id: str):
    db = get_database()
    # Simple implementation: we'll store bookmarks in user_bookmarks collection
    existing = await db["user_bookmarks"].find_one({"user_id": user_id, "question_id": question_id})
    if existing:
        await db["user_bookmarks"].delete_one({"_id": existing["_id"]})
        return False # unbookmarked
    else:
        await db["user_bookmarks"].insert_one({"user_id": user_id, "question_id": question_id})
        return True # bookmarked

async def get_user_bookmarked_questions(user_id: str):
    db = get_database()
    bookmarks = []
    async for doc in db["user_bookmarks"].find({"user_id": user_id}):
        bookmarks.append(doc["question_id"])
    return bookmarks
