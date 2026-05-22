from motor.motor_asyncio import AsyncIOMotorDatabase

from src.schemas.models import (
    EmbeddingsModelsResponse
)


async def get_available_embedding_models(
    db: AsyncIOMotorDatabase
) -> list[EmbeddingsModelsResponse]:
    models_db = db["openrouter_available_embedding_models"].find({})

    models: list[EmbeddingsModelsResponse] = []

    async for model in models_db:
        models.append(
            EmbeddingsModelsResponse(
                id=model["model_id"],
                name=model["name"],
                supported_parameters=model["supported_parameters"]
            )
        )

    return models
