from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase

from src.models.documents import DocumentChunk, EmbeddingChunkInDB
from src.models.embeddings import EmbeddingResult

BATCH_SIZE = 500


def get_vector_search_index_name(collection: str) -> str:
    return f"vector_index_{collection}"


async def add_new_embedding(
    embeddings: list[EmbeddingResult],
    user_id: str,
    model_id: str,
    db: AsyncIOMotorDatabase,
    session: AsyncIOMotorClientSession | None = None,
) -> str:
    user_id = ObjectId(user_id)
    dimensions = embeddings[0].dimensions
    collection = f"documents_{dimensions}"

    documents: list[dict[str, Any]] = []

    for embedding in embeddings:
        document = embedding.model_dump()
        document["user_id"] = user_id
        document["model_id"] = model_id

        documents.append(document)

    for i in range(0, len(documents), BATCH_SIZE):
        batch = documents[i : i + BATCH_SIZE]

        await db[collection].insert_many(documents=batch, session=session)

    return collection


async def delete_embeddings_by_filename(
    user_id: str, filename: str, collection: str, db: AsyncIOMotorDatabase
) -> None:
    client = db.client

    async with await client.start_session() as session:
        async with session.start_transaction():
            await db[collection].delete_many(
                {"user_id": ObjectId(user_id), "meta_data.filename": filename},
                session=session,
            )


async def get_embeddings(
    user_id: str, filename: str, collection: str, db: AsyncIOMotorDatabase
) -> list[EmbeddingChunkInDB]:
    cursor = db[collection].find(
        {"user_id": ObjectId(user_id), "meta_data.filename": filename}
    )

    embeddings_data: list[EmbeddingChunkInDB] = []

    async for doc in cursor:
        embeddings_data.append(
            EmbeddingChunkInDB(
                chunk=DocumentChunk(
                    chunk=doc["chunk"], id=str(doc["_id"]), meta_data=doc.get("meta_data")
                ),
                embeddings=doc["embeddings"],
            )
        )

    return embeddings_data
