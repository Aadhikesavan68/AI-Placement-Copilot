from database.mongo import get_database
from datetime import datetime
import uuid
from typing import List, Optional

async def create_job_description(jd_data: dict) -> dict:
    db = get_database()
    if "id" not in jd_data or not jd_data["id"]:
        jd_data["id"] = str(uuid.uuid4())
    if "upload_date" not in jd_data or not jd_data["upload_date"]:
        jd_data["upload_date"] = datetime.utcnow()
    
    await db["job_descriptions"].insert_one(jd_data)
    if "_id" in jd_data:
        del jd_data["_id"]
    return jd_data

async def get_latest_job_description(user_id: str) -> Optional[dict]:
    db = get_database()
    doc = await db["job_descriptions"].find_one(
        {"user_id": user_id},
        sort=[("upload_date", -1)]
    )
    if doc:
        doc["id"] = str(doc.get("id", doc.get("_id")))
        if "_id" in doc:
            del doc["_id"]
        return doc
    return None

async def get_job_descriptions_by_user(user_id: str) -> List[dict]:
    db = get_database()
    job_descriptions = []
    cursor = db["job_descriptions"].find({"user_id": user_id}).sort("upload_date", -1)
    async for document in cursor:
        document["id"] = str(document.get("id", document.get("_id")))
        if "_id" in document:
            del document["_id"]
        job_descriptions.append(document)
    return job_descriptions

async def get_job_description_by_id(jd_id: str, user_id: str) -> Optional[dict]:
    db = get_database()
    doc = await db["job_descriptions"].find_one({"id": jd_id, "user_id": user_id})
    if not doc:
        from bson import ObjectId
        try:
            doc = await db["job_descriptions"].find_one({"_id": ObjectId(jd_id), "user_id": user_id})
        except Exception:
            pass
            
    if doc:
        doc["id"] = str(doc.get("id", doc.get("_id")))
        if "_id" in doc:
            del doc["_id"]
        return doc
    return None

async def delete_job_description_by_id(jd_id: str, user_id: str) -> bool:
    db = get_database()
    result = await db["job_descriptions"].delete_one({"id": jd_id, "user_id": user_id})
    if result.deleted_count == 0:
        from bson import ObjectId
        try:
            result = await db["job_descriptions"].delete_one({"_id": ObjectId(jd_id), "user_id": user_id})
        except Exception:
            pass
    return result.deleted_count > 0
