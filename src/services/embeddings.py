from typing import Any

import httpx
from fastapi import HTTPException, status

from src.core.settings import get_settings
from src.models.documents import DocumentChunk
from src.models.embeddings import EmbeddingResult
from src.utils.batch_utils import batched


async def generate_embedding(
    model_id: str, params: dict[str, Any], chunks: list[DocumentChunk]
) -> list[EmbeddingResult]:
    if not chunks:
        return []

    all_results: list[EmbeddingResult] = []

    for batch_chunk in batched(chunks, 64):
        texts = [chunk.chunk for chunk in batch_chunk]

        embeddings_list = await generate_text_embedding(
            model_id=model_id, params=params, texts=texts
        )

        if len(embeddings_list) != len(batch_chunk):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Mismatch between chunks and embeddings",
            )

        for chunk, embeddings in zip(batch_chunk, embeddings_list):
            all_results.append(
                EmbeddingResult(
                    embeddings=embeddings,
                    dimensions=len(embeddings),
                    chunk=chunk.chunk,
                    chunk_id=chunk.id,
                    meta_data=chunk.meta_data,
                )
            )

    return all_results


async def generate_text_embedding(
    model_id: str, params: dict[str, Any], texts: list[str]
) -> list[list[float]]:
    headers = {
        "Authorization": f"Bearer {get_settings().OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {"model": model_id, "input": texts, **params}

    timeout = httpx.Timeout(connect=5.0, read=120.0, write=30.0, pool=10.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url="https://openrouter.ai/api/v1/embeddings",
                json=payload,
                headers=headers,
            )

            if response.status_code >= 400:
                raise HTTPException(response.status_code, detail=response.json())
    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Embedding provider timeout",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json(),
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

    body = response.json()

    if body is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="It was not possible to generate the embeddings",
        )

    data = body.get("data", None)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="It was not possible to generate the embeddings",
        )

    embeddings: list[list[float]] = []

    for item in data:
        embedding = item.get("embedding", None)

        if embedding is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid embedding response",
            )

        embeddings.append(embedding)

    return embeddings
