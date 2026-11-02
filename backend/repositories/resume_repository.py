from database.mongo import get_database
from schemas.resume_schema import ResumeCreate, ResumeInDB
from datetime import datetime
from bson import ObjectId
import uuid

async def create_resume(resume_data: dict):
    db = get_database()
    resume_data["id"] = str(uuid.uuid4())
    resume_data["upload_date"] = datetime.utcnow()
    await db["resume_history"].insert_one(resume_data)
    if "_id" in resume_data:
        del resume_data["_id"]
    return resume_data

async def get_resumes_by_user(user_id: str):
    db = get_database()
    resumes = []
    cursor = db["resume_history"].find({"user_id": user_id}).sort("upload_date", -1)
    async for document in cursor:
        document["id"] = str(document.get("id", document["_id"]))
        if "_id" in document:
            del document["_id"]
        resumes.append(document)
    return resumes

async def get_resume_by_id(resume_id: str, user_id: str):
    db = get_database()
    try:
        resume = await db["resume_history"].find_one({"_id": ObjectId(resume_id), "user_id": user_id})
        if not resume:
            resume = await db["resume_history"].find_one({"id": resume_id, "user_id": user_id})
        if resume:
            resume["id"] = str(resume.get("id", resume["_id"]))
            if "_id" in resume:
                del resume["_id"]
            return resume
    except Exception:
        resume = await db["resume_history"].find_one({"id": resume_id, "user_id": user_id})
        if resume:
            resume["id"] = str(resume.get("id", resume["_id"]))
            if "_id" in resume:
                del resume["_id"]
            return resume
    return None

async def delete_resume_by_id(resume_id: str, user_id: str):
    db = get_database()
    try:
        res = await db["resume_history"].delete_one({"_id": ObjectId(resume_id), "user_id": user_id})
        if res.deleted_count > 0:
            return True
    except Exception:
        pass
    res2 = await db["resume_history"].delete_one({"id": resume_id, "user_id": user_id})
    return res2.deleted_count > 0

async def update_resume_by_id(resume_id: str, user_id: str, updates: dict):
    db = get_database()
    query = {"user_id": user_id}
    try:
        query["_id"] = ObjectId(resume_id)
        result = await db["resume_history"].update_one(query, {"$set": updates})
        if result.matched_count > 0:
            return await get_resume_by_id(resume_id, user_id)
    except Exception:
        pass

    result = await db["resume_history"].update_one(
        {"id": resume_id, "user_id": user_id}, {"$set": updates}
    )
    if result.matched_count > 0:
        return await get_resume_by_id(resume_id, user_id)
    return None
