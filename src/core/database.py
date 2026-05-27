from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.core.settings import get_settings

MONGODB_URL = get_settings().MONGODB_URL

client = AsyncIOMotorClient(MONGODB_URL)

database = client["CortexFlow"]


async def get_db() -> AsyncIOMotorDatabase:
    return database


async def get_agent_db() -> AsyncIOMotorDatabase:
    return client["agno"]
