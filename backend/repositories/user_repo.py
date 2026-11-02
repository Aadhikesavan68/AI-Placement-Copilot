from datetime import datetime
import uuid
from bson import ObjectId
from bson.errors import InvalidId

from database.mongo import get_database
from schemas.user_schema import UserCreate


def serialize_user(user: dict | None) -> dict | None:
    """Normalize a Mongo user document for JWT + API responses."""
    if not user:
        return None

    public_id = user.get("id")
    if not public_id and user.get("_id") is not None:
        public_id = str(user["_id"])

    return {
        "id": str(public_id),
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }


def _with_password(user: dict | None) -> dict | None:
    if not user:
        return None
    normalized = serialize_user(user)
    normalized["hashed_password"] = user.get("hashed_password")
    return normalized


async def get_user_by_email(email: str):
    db = get_database()
    user = await db["users"].find_one({"email": email})
    return _with_password(user)


async def get_user_by_id(user_id: str):
    db = get_database()
    if not user_id:
        return None

    user = await db["users"].find_one({"id": user_id})
    if not user:
        try:
            user = await db["users"].find_one({"_id": ObjectId(user_id)})
        except (InvalidId, TypeError):
            user = None
    return _with_password(user)


async def create_user(user: UserCreate):
    db = get_database()
    now = datetime.utcnow()
    new_user = {
        "id": str(uuid.uuid4()),
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "hashed_password": user.password,
        "created_at": now,
        "updated_at": now,
    }
    await db["users"].insert_one(new_user)
    return _with_password(new_user)
