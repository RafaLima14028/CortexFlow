from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.db.mongo import MongoDb

from typing import Any

from src.core.settings import get_settings


def get_conversation_agent(
    api_key: str,
    user_id: str,
    session_id: str,
    model_id: str,
    model_params: dict[str, Any]
) -> Agent:
    model_provider = OpenRouter(
        id=model_id,
        api_key=api_key,
        **model_params
    )

    mongodb_storage = MongoDb(
        db_url=get_settings().MONGODB_URL
    )

    return Agent(
        model=model_provider,
        user_id=user_id,
        session_id=session_id,
        db=mongodb_storage,
        markdown=True,
        add_history_to_context=True
    )
