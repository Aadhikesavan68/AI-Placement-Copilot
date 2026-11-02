from datetime import datetime
from typing import Optional

from bson import ObjectId
from pymongo import ReturnDocument

from database.mongo import get_database


def _serialize(document: Optional[dict]) -> Optional[dict]:
    if not document:
        return None
    document["id"] = str(document.pop("_id"))
    return document


async def save_plan(plan: dict) -> dict:
    result = await get_database()["learning_plans"].insert_one(plan)
    plan["_id"] = result.inserted_id
    return _serialize(plan)


async def get_plan(plan_id: str, user_id: str) -> Optional[dict]:
    query = {"user_id": user_id}
    try:
        query["_id"] = ObjectId(plan_id)
        document = await get_database()["learning_plans"].find_one(query)
    except Exception:
        document = await get_database()["learning_plans"].find_one({"id": plan_id, "user_id": user_id})
    return _serialize(document)


async def get_plan_for_analysis(analysis_id: str, user_id: str) -> Optional[dict]:
    document = await get_database()["learning_plans"].find_one(
        {"analysis_id": analysis_id, "user_id": user_id},
        sort=[("updated_at", -1)],
    )
    return _serialize(document)


async def update_plan(plan_id: str, user_id: str, changes: dict) -> Optional[dict]:
    try:
        result = await get_database()["learning_plans"].find_one_and_update(
            {"_id": ObjectId(plan_id), "user_id": user_id},
            {"$set": changes},
            return_document=ReturnDocument.AFTER,
        )
    except Exception:
        result = await get_database()["learning_plans"].find_one_and_update(
            {"id": plan_id, "user_id": user_id},
            {"$set": changes},
            return_document=ReturnDocument.AFTER,
        )
    return _serialize(result)


async def save_mock_test(test: dict) -> dict:
    result = await get_database()["learning_mock_tests"].insert_one(test)
    test["_id"] = result.inserted_id
    return _serialize(test)


async def get_mock_test(test_id: str, user_id: str) -> Optional[dict]:
    try:
        document = await get_database()["learning_mock_tests"].find_one(
            {"_id": ObjectId(test_id), "user_id": user_id}
        )
    except Exception:
        document = await get_database()["learning_mock_tests"].find_one(
            {"id": test_id, "user_id": user_id}
        )
    return _serialize(document)


async def update_mock_test(test_id: str, user_id: str, changes: dict) -> Optional[dict]:
    try:
        result = await get_database()["learning_mock_tests"].find_one_and_update(
            {"_id": ObjectId(test_id), "user_id": user_id},
            {"$set": changes},
            return_document=ReturnDocument.AFTER,
        )
    except Exception:
        result = await get_database()["learning_mock_tests"].find_one_and_update(
            {"id": test_id, "user_id": user_id},
            {"$set": changes},
            return_document=ReturnDocument.AFTER,
        )
    return _serialize(result)
