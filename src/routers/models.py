import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.database import get_db
from src.core.settings import get_settings
from src.schemas.models import (
    ChatModelsResponse,
    EmbeddingsModelsResponse,
    RerankingModelsResponse,
)
from src.services.database.models_db import get_available_embedding_models

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/embeddings", response_model=list[EmbeddingsModelsResponse])
async def get_embeddings_from_openrouter(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_available_embedding_models(db=db)


@router.get("/reranking", response_model=list[RerankingModelsResponse])
async def get_reranking_from_openrouter():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url="https://openrouter.ai/api/v1/models",
                headers={
                    "Authorization": f"Bearer {get_settings().OPENROUTER_API_KEY}"
                },
            )

            response.raise_for_status()

            data = response.json()["data"]
        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error searching for models in OpenRouter",
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Not possible connect to OpenRouter",
            )

    models: list[RerankingModelsResponse] = []

    for model in data:
        model_id = model.get("id", "").lower()
        name = model.get("name", "").lower()

        architecture = model.get("architecture", {})
        modality = architecture.get("modality", "").lower()

        supported_parameters = model.get("supported_parameters", [])

        is_reranker = any(
            [
                "rerank" in model_id,
                "rerank" in name,
                "text->text" in modality,
                "documents" in supported_parameters,
            ]
        )

        if is_reranker:
            models.append(
                RerankingModelsResponse(
                    id=model["id"],
                    name=model["name"],
                    supported_parameters=model["supported_parameters"],
                )
            )

    return models


@router.get("/chat", response_model=list[ChatModelsResponse])
async def get_chat_models():
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(
                url="https://openrouter.ai/api/v1/models",
                headers={
                    "Authorization": f"Bearer {get_settings().OPENROUTER_API_KEY}"
                },
            )

            response.raise_for_status()

            data = response.json()["data"]
        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error searching for models in OpenRouter",
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Not possible connect to OpenRouter",
            )

    chat_models: list[ChatModelsResponse] = []

    for model in data:
        architecture = model.get("architecture", {})

        input_modalities = architecture.get("input_modalities", [])

        output_modalities = architecture.get("output_modalities", [])

        if "text" in input_modalities and "text" in output_modalities:
            chat_models.append(
                ChatModelsResponse(
                    id=model["id"],
                    name=model["name"],
                    supported_parameters=model["supported_parameters"],
                )
            )

    return chat_models
