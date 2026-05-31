import json
from typing import Any

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import OperationFailure

from src.services.database.db import validate_object_id
from src.services.database.embeddings_db import get_vector_search_index_name
from src.services.embeddings import generate_text_embedding


async def get_vector_search_index_metadata(
    collection: str, db: AsyncIOMotorDatabase
) -> dict[str, Any]:
    expected_index_name = get_vector_search_index_name(collection)

    try:
        cursor = db[collection].aggregate([{"$listSearchIndexes": {}}])

        fallback_index: dict[str, Any] | None = None

        async for index in cursor:
            if index.get("type") != "vectorSearch":
                continue

            if fallback_index is None:
                fallback_index = index

            if index.get("name") == expected_index_name:
                return {
                    "name": expected_index_name,
                    "filter_paths": extract_vector_filter_paths(index),
                }

        if fallback_index is not None:
            return {
                "name": fallback_index["name"],
                "filter_paths": extract_vector_filter_paths(fallback_index),
            }
    except OperationFailure:
        pass

    return {"name": expected_index_name, "filter_paths": set()}


def extract_vector_filter_paths(index: dict[str, Any]) -> set[str]:
    definition = index.get("latestDefinition") or index.get("definition") or {}
    fields = definition.get("fields", [])

    return {
        field["path"]
        for field in fields
        if field.get("type") == "filter" and "path" in field
    }


async def search_user_vector_documents(
    user_id: str, query: str, limit: int, db: AsyncIOMotorDatabase
) -> list[dict[str, Any]]:
    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="rag_limit must be greater than zero",
        )

    user_object_id = validate_object_id(user_id)
    documents_cursor = db["documents"].find({"user_id": user_object_id})

    groups: dict[str, dict[str, Any]] = {}

    async for document in documents_cursor:
        collection = document["collection"]
        model_id = document["model_id"]
        params = document.get("embedding_model_params", {})

        key = json.dumps(
            {"collection": collection, "model_id": model_id, "params": params},
            sort_keys=True,
            default=str,
        )

        groups[key] = {"collection": collection, "model_id": model_id, "params": params}

    results: list[dict[str, Any]] = []
    embedding_cache: dict[str, list[float]] = {}

    for group in groups.values():
        model_id = group["model_id"]
        params = group["params"]
        collection = group["collection"]
        index_metadata = await get_vector_search_index_metadata(
            collection=collection, db=db
        )
        filter_paths = index_metadata["filter_paths"]
        vector_filter = {"user_id": user_object_id}

        if "model_id" in filter_paths:
            vector_filter["model_id"] = model_id

        embedding_key = json.dumps(
            {"model_id": model_id, "params": params}, sort_keys=True, default=str
        )

        if embedding_key not in embedding_cache:
            embedding_cache[embedding_key] = (
                await generate_text_embedding(
                    model_id=model_id, params=params, texts=[query]
                )
            )[0]

        pipeline = [
            {
                "$vectorSearch": {
                    "index": index_metadata["name"],
                    "path": "embeddings",
                    "queryVector": embedding_cache[embedding_key],
                    "numCandidates": limit * 10,
                    "limit": limit,
                    "filter": vector_filter,
                }
            }
        ]

        if "model_id" not in filter_paths:
            pipeline.append({"$match": {"model_id": model_id}})

        pipeline.append(
            {
                "$project": {
                    "_id": 0,
                    "chunk": 1,
                    "chunk_id": 1,
                    "meta_data": 1,
                    "model_id": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            }
        )

        cursor = db[collection].aggregate(pipeline)

        async for result in cursor:
            results.append(result)

    results.sort(key=lambda item: item.get("score", 0), reverse=True)
    return results[:limit]


def format_vector_search_results(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No evidence was found in the user's documents."

    formatted_results: list[str] = []

    for index, result in enumerate(results, start=1):
        meta_data = result.get("meta_data") or {}
        source = meta_data.get("filename", "unknown source")
        score = result.get("score", 0)
        chunk = result.get("chunk", "")

        formatted_results.append(
            f"[{index}] Source: {source}\nScore: {score:.4f}\nText:\n{chunk}"
        )

    return "\n\n".join(formatted_results)


def build_search_user_documents_tool(
    user_id: str, db: AsyncIOMotorDatabase, default_limit: int = 5
):
    async def search_user_documents(query: str, limit: int = default_limit) -> str:
        effective_limit = min(max(limit or default_limit, 1), 20)

        results = await search_user_vector_documents(
            user_id=user_id, query=query, limit=effective_limit, db=db
        )

        return format_vector_search_results(results)

    return search_user_documents
