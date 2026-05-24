from typing import Any
import httpx
from fastapi import HTTPException, status

from src.core.settings import get_settings
from src.schemas.embeddings import EmbeddingsResults
from src.schemas.documents import ChunkingResponse


async def generate_embedding(
    model_id: str,
    params: dict[str, Any],
    chunks: list[ChunkingResponse]
) -> list[EmbeddingsResults]:
    list_embeddings: list[EmbeddingsResults] = []

    for chunk in chunks:
        embeddings = await generate_text_embedding(
            model_id=model_id,
            params=params,
            text=chunk.chunk
        )

        list_embeddings.append(
            EmbeddingsResults(
                embeddings=embeddings,
                dimensions=len(embeddings),
                chunk=chunk.chunk,
                chunk_id=chunk.id,
                meta_data=chunk.meta_data
            )
        )

    return list_embeddings


async def generate_text_embedding(
    model_id: str,
    params: dict[str, Any],
    text: str
) -> list[float]:
    headers = {
        "Authorization": f"Bearer {get_settings().OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_id,
        "input": text,
        **params
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url="https://openrouter.ai/api/v1/embeddings",
            json=payload,
            headers=headers
        )

        if response.status_code >= 400:
            raise HTTPException(
                response.status_code,
                detail=response.json()
            )

    data = response.json().get("data", None)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="It was not possible to generate the embeddings"
        )

    embeddings = data[0].get("embedding", None)

    if embeddings is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="It was not possible to generate the embeddings"
        )

    return embeddings
