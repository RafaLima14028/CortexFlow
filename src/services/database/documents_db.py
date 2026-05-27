from typing import Any

from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase

from src.schemas.documents import DocumentResponse, DocumentResponseInternal
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
) -> list[DocumentResponse]:
    documents = db["documents"].find({"user_id": validate_object_id(user_id)})

    list_documents: list[DocumentResponse] = []

    async for document in documents:
        list_documents.append(
            DocumentResponse(
                id=str(document["_id"]),
                filename=document["filename"],
                model_id=document["model_id"],
            )
        )

    return list_documents


async def get_documents_by_user_id_and_document_id(
    user_id: str, document_id: str, db: AsyncIOMotorDatabase
) -> tuple[DocumentResponse, str] | None:
    document = await db["documents"].find_one(
        {"user_id": validate_object_id(user_id), "_id": validate_object_id(document_id)}
    )

    if document is not None:
        return (
            DocumentResponse(
                id=str(document["_id"]),
                filename=document["filename"],
                model_id=document["model_id"],
            ),
            document["collection"],
        )

    return None


async def delete_document_by_id(
    user_id: str, document_id: str, db: AsyncIOMotorDatabase
) -> DocumentResponseInternal | None:
    deleted_doc = await db["documents"].find_one_and_delete(
        {"user_id": validate_object_id(user_id), "_id": validate_object_id(document_id)}
    )

    if deleted_doc is not None:
        return DocumentResponseInternal(
            id=str(deleted_doc["_id"]),
            filename=deleted_doc["filename"],
            model_id=deleted_doc["model_id"],
            collection=deleted_doc["collection"],
        )

    return None
