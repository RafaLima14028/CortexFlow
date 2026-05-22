from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException, status

from src.schemas.chat import (
    ChatResponseDB
)


async def add_new_message(
    content: str,
    role: str,
    user_id: str,
    chat_id: str,
    db: AsyncIOMotorDatabase
) -> None:
    document = {
        "content": content,
        "role": role,
        "user_id": ObjectId(user_id),
        "chat_id": chat_id
    }

    await db["chat_history"].insert_one(
        document=document
    )

    return


async def get_all_id_by_user_id(
    user_id: str,
    db: AsyncIOMotorDatabase,
    limit: int = 10,
    skip: int = 0
) -> list[str]:
    chat_ids_list = await db["agno_sessions"].aggregate([
        {
            "$match": {
                "user_id": {
                    "$eq": user_id
                }
            }
        },
        {
            "$sort": {
                "updated_at": -1
            }
        },
        {
            "$group": {
                "_id": "$session_id",
                "updated_at": {
                    "$first": "$updated_at"
                }
            }
        },
        {
            "$skip": skip
        },
        {
            "$limit": limit
        },
        {
            "$project": {
                "_id": 0,
                "chat_id": "$_id"
            }
        }
    ]).to_list(length=limit)

    return [
        str(doc["chat_id"]) for doc in chat_ids_list
    ]


async def get_messages_by_chat_id(
    chat_id: str,
    user_id: str,
    db: AsyncIOMotorDatabase
) -> tuple[list[ChatResponseDB], bool]:
    message = await db["agno_sessions"].find_one({
        "user_id": user_id,
        "session_id": chat_id
    })

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Messages not found"
        )

    all_messages: list[ChatResponseDB] = []

    index: int = 0

    for run in message["runs"]:
        for message in run["messages"]:
            all_messages.append(
                ChatResponseDB(
                    index=index,
                    content=message["content"],
                    role=message["role"]
                )
            )

            index += 1

    return all_messages
