from motor.motor_asyncio import AsyncIOMotorDatabase

from src.models.auth import UserRegister, UserResponse
from src.services.database.db import validate_object_id


async def user_exists_by_id(user_id: str, db: AsyncIOMotorDatabase) -> bool:
    user = await db["users"].find_one({"_id": validate_object_id(user_id)})

    return user is not None


async def get_user_by_email(
    email: str, db: AsyncIOMotorDatabase
) -> UserResponse | None:
    user_dict = await db["users"].find_one({"email": email})

    if not user_dict:
        return None

    user_dict["_id"] = str(user_dict["_id"])

    return UserResponse(**user_dict)


async def add_new_user(user: UserRegister, db: AsyncIOMotorDatabase) -> None:
    await db["users"].insert_one(document=user.model_dump())
