from motor.motor_asyncio import AsyncIOMotorDatabase

from src.models.provider_models import AvailableEmbeddingModelInDB


async def get_available_embedding_models(
    db: AsyncIOMotorDatabase,
) -> list[AvailableEmbeddingModelInDB]:
    models_db = db["openrouter_available_embedding_models"].find({})

    models: list[AvailableEmbeddingModelInDB] = []

    async for model in models_db:
        models.append(
            AvailableEmbeddingModelInDB(
                id=model["model_id"],
                name=model["name"],
                supported_parameters=model.get("supported_parameters"),
            )
        )

    return models
