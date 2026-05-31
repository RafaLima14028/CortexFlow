from typing import Any

from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase

from src.models.documents import DocumentInDB
from src.services.database.db import validate_object_id


async def add_new_user_document(
    user_id: str,
    filename: str,
    model_id: str,
    embedding_model_params: dict[str, Any],
    collection_name: str,
    db: AsyncIOMotorDatabase,
    session: AsyncIOMotorClientSession | None = None,
) -> None:
    await db["documents"].insert_one(
        {
            "user_id": validate_object_id(user_id),
            "filename": filename,
            "model_id": model_id,
            "embedding_model_params": embedding_model_params,
            "collection": collection_name,
        },
        session=session,
    )


async def get_documents_by_user_id(
    user_id: str, db: AsyncIOMotorDatabase
) -> list[DocumentInDB]:
    documents = db["documents"].find({"user_id": validate_object_id(user_id)})

    list_documents: list[DocumentInDB] = []

    async for document in documents:
        list_documents.append(
            DocumentInDB(
                id=str(document["_id"]),
                user_id=str(document["user_id"]),
                filename=document["filename"],
                model_id=document["model_id"],
                embedding_model_params=document.get("embedding_model_params", {}),
                collection=document["collection"],
            )
        )

    return list_documents


async def get_documents_by_user_id_and_document_id(
    user_id: str, document_id: str, db: AsyncIOMotorDatabase
) -> DocumentInDB | None:
    document = await db["documents"].find_one(
        {"user_id": validate_object_id(user_id), "_id": validate_object_id(document_id)}
    )

    if document is not None:
        return DocumentInDB(
            id=str(document["_id"]),
            user_id=str(document["user_id"]),
            filename=document["filename"],
            model_id=document["model_id"],
            embedding_model_params=document.get("embedding_model_params", {}),
            collection=document["collection"],
        )

    return None


async def delete_document_by_id(
    user_id: str, document_id: str, db: AsyncIOMotorDatabase
) -> DocumentInDB | None:
    deleted_doc = await db["documents"].find_one_and_delete(
        {"user_id": validate_object_id(user_id), "_id": validate_object_id(document_id)}
    )

    if deleted_doc is not None:
        return DocumentInDB(
            id=str(deleted_doc["_id"]),
            user_id=str(deleted_doc["user_id"]),
            filename=deleted_doc["filename"],
            model_id=deleted_doc["model_id"],
            embedding_model_params=deleted_doc.get("embedding_model_params", {}),
            collection=deleted_doc["collection"],
        )

    return None
