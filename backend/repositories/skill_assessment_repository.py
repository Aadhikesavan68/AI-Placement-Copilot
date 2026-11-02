from datetime import datetime
from typing import Optional
import uuid

from bson import ObjectId
from database.mongo import get_database


def _serialize(document: Optional[dict]) -> Optional[dict]:
    if not document:
        return None
    document = dict(document)
    identifier = document.pop("_id", None)
    document["id"] = str(document.get("id") or identifier)
    return document


async def upsert_candidate_skills(user_id: str, skills: list[dict]) -> list[dict]:
    collection = get_database()["candidate_skills"]
    for skill in skills:
        await collection.update_one(
            {"user_id": user_id, "skill": skill["skill"]},
            {"$set": {**skill, "user_id": user_id}, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True,
        )
    return await list_candidate_skills(user_id)


async def list_candidate_skills(user_id: str) -> list[dict]:
    cursor = get_database()["candidate_skills"].find({"user_id": user_id}).sort("skill", 1)
    return [_serialize(item) async for item in cursor]


async def get_candidate_skill(user_id: str, skill: str) -> Optional[dict]:
    return _serialize(await get_database()["candidate_skills"].find_one({"user_id": user_id, "skill": skill}))


async def update_candidate_skill(user_id: str, skill: str, changes: dict) -> None:
    await get_database()["candidate_skills"].update_one(
        {"user_id": user_id, "skill": skill},
        {"$set": changes},
        upsert=True,
    )


async def save_session(session: dict) -> dict:
    session = {**session, "id": str(uuid.uuid4()), "created_at": datetime.utcnow()}
    await get_database()["skill_assessment_sessions"].insert_one(session)
    return session


async def get_session(session_id: str, user_id: str) -> Optional[dict]:
    query = {"user_id": user_id}
    try:
        query["_id"] = ObjectId(session_id)
        document = await get_database()["skill_assessment_sessions"].find_one(query)
    except Exception:
        document = await get_database()["skill_assessment_sessions"].find_one(
            {"id": session_id, "user_id": user_id}
        )
    return _serialize(document)


async def update_session(session_id: str, user_id: str, changes: dict) -> Optional[dict]:
    session = await get_session(session_id, user_id)
    if not session:
        return None
    await get_database()["skill_assessment_sessions"].update_one(
        {"id": session["id"], "user_id": user_id},
        {"$set": changes},
    )
    return await get_session(session["id"], user_id)


async def save_assessment(result: dict) -> dict:
    result = {**result, "id": str(uuid.uuid4()), "created_at": datetime.utcnow()}
    await get_database()["skill_assessments"].insert_one(result)
    return result


async def list_assessments(user_id: str, skill: Optional[str] = None) -> list[dict]:
    query = {"user_id": user_id}
    if skill:
        query["skill"] = skill
    cursor = get_database()["skill_assessments"].find(query).sort("created_at", -1)
    return [_serialize(item) async for item in cursor]


async def get_latest_assessment(user_id: str, skill: str) -> Optional[dict]:
    document = await get_database()["skill_assessments"].find_one(
        {"user_id": user_id, "skill": skill},
        sort=[("created_at", -1)],
    )
    return _serialize(document)


async def get_latest_assessments(user_id: str) -> list[dict]:
    skills = await list_candidate_skills(user_id)
    results = []
    for skill in skills:
        latest = await get_latest_assessment(user_id, skill["skill"])
        if latest:
            results.append(latest)
    return results
