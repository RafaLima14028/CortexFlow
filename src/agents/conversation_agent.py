from typing import Any
from pathlib import Path

from fastapi import HTTPException, status
from agno.agent import Agent
from agno.db.mongo import MongoDb
from agno.models.openrouter import OpenRouter
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.settings import get_settings
from src.services.vector_search import build_search_user_documents_tool

CURRENT_DIR = Path(__file__).resolve().parent

PROMPT_FILE_PATH = CURRENT_DIR / "prompt" / "conversation_agent_prompt.md"


def get_conversation_prompt() -> str:
    try:
        return PROMPT_FILE_PATH.read_text(encoding="utf-8")
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The agent could not be loaded",
        )


def get_conversation_agent(
    api_key: str,
    user_id: str,
    session_id: str,
    model_id: str,
    model_params: dict[str, Any],
    rag_db: AsyncIOMotorDatabase | None = None,
    use_rag: bool = True,
    rag_limit: int = 5,
) -> Agent:
    model_provider = OpenRouter(id=model_id, api_key=api_key, **model_params)

    mongodb_storage = MongoDb(db_url=get_settings().MONGODB_URL)

    tools = []

    if use_rag and rag_db is not None:
        tools.append(
            build_search_user_documents_tool(
                user_id=user_id, db=rag_db, default_limit=rag_limit
            )
        )

    instructions: str = get_conversation_prompt()

    return Agent(
        model=model_provider,
        user_id=user_id,
        session_id=session_id,
        db=mongodb_storage,
        tools=tools,
        instructions=instructions,
        markdown=True,
        add_history_to_context=True,
        reasoning_max_steps=7,
    )
