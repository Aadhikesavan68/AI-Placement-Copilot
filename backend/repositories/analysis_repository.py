from database.mongo import get_database
from datetime import datetime
from bson import ObjectId
from typing import List, Optional

async def save_ats_analysis(analysis_data: dict) -> dict:
    db = get_database()
    analysis_data["created_at"] = datetime.utcnow()
    result = await db["ats_analyses"].insert_one(analysis_data)
    analysis_data["id"] = str(result.inserted_id)
    if "_id" in analysis_data:
        del analysis_data["_id"]
    return analysis_data

async def get_user_ats_analyses(user_id: str, search: str = "", sort_by: str = "date_desc") -> list:
    db = get_database()
    query = {"user_id": user_id}
    
    if search and search.strip():
        search_regex = {"$regex": search.strip(), "$options": "i"}
        query["$or"] = [
            {"resume_name": search_regex},
            {"company_name": search_regex},
            {"role_title": search_regex},
            {"jd_data.role": search_regex},
            {"jd_data.company_name": search_regex}
        ]
        
    sort_criteria = ("created_at", -1)
    if sort_by == "date_asc":
        sort_criteria = ("created_at", 1)
    elif sort_by == "match_desc":
        sort_criteria = ("match_score", -1)
    elif sort_by == "match_asc":
        sort_criteria = ("match_score", 1)
    elif sort_by == "ats_desc":
        sort_criteria = ("ats_score", -1)
    elif sort_by == "ats_asc":
        sort_criteria = ("ats_score", 1)

    analyses = []
    async for doc in db["ats_analyses"].find(query).sort([sort_criteria]):
        doc["id"] = str(doc["_id"])
        if "_id" in doc:
            del doc["_id"]
        analyses.append(doc)
    return analyses

async def get_ats_analysis_by_id(analysis_id: str, user_id: str) -> Optional[dict]:
    db = get_database()
    try:
        # Try ObjectId first
        doc = await db["ats_analyses"].find_one({"_id": ObjectId(analysis_id), "user_id": user_id})
        if not doc:
            doc = await db["ats_analyses"].find_one({"id": analysis_id, "user_id": user_id})
        if doc:
            doc["id"] = str(doc["_id"])
            if "_id" in doc:
                del doc["_id"]
            return doc
    except Exception:
        doc = await db["ats_analyses"].find_one({"id": analysis_id, "user_id": user_id})
        if doc:
            doc["id"] = str(doc["_id"])
            if "_id" in doc:
                del doc["_id"]
            return doc
    return None

async def delete_ats_analysis_by_id(analysis_id: str, user_id: str) -> bool:
    db = get_database()
    try:
        res = await db["ats_analyses"].delete_one({"_id": ObjectId(analysis_id), "user_id": user_id})
        if res.deleted_count > 0:
            return True
    except Exception:
        pass
    res2 = await db["ats_analyses"].delete_one({"id": analysis_id, "user_id": user_id})
    return res2.deleted_count > 0

async def get_job_description_by_id(jd_id: str, user_id: str) -> Optional[dict]:
    db = get_database()
    try:
        doc = await db["job_descriptions"].find_one({"_id": ObjectId(jd_id), "user_id": user_id})
        if not doc:
            doc = await db["job_descriptions"].find_one({"id": jd_id, "user_id": user_id})
        if doc and "_id" in doc:
            del doc["_id"]
        return doc
    except Exception:
        doc = await db["job_descriptions"].find_one({"id": jd_id, "user_id": user_id})
        if doc and "_id" in doc:
            del doc["_id"]
        return doc

# Legacy helpers for backward compatibility
async def save_analysis(analysis_data: dict) -> dict:
    return await save_ats_analysis(analysis_data)

async def get_user_analyses(user_id: str) -> list:
    return await get_user_ats_analyses(user_id)

async def get_analysis_by_id(analysis_id: str, user_id: str) -> dict:
    return await get_ats_analysis_by_id(analysis_id, user_id)
