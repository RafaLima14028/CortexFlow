from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.db.mongo import MongoDb

from typing import Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.settings import get_settings
from src.services.vector_search import build_search_user_documents_tool


def get_conversation_agent(
    api_key: str,
    user_id: str,
    session_id: str,
    model_id: str,
    model_params: dict[str, Any],
    rag_db: AsyncIOMotorDatabase | None = None,
    use_rag: bool = True,
    rag_limit: int = 5
) -> Agent:
    model_provider = OpenRouter(
        id=model_id,
        api_key=api_key,
        **model_params
    )

    mongodb_storage = MongoDb(
        db_url=get_settings().MONGODB_URL
    )

    tools = []

    if use_rag and rag_db is not None:
        tools.append(
            build_search_user_documents_tool(
                user_id=user_id,
                db=rag_db,
                default_limit=rag_limit
            )
        )

    return Agent(
        model=model_provider,
        user_id=user_id,
        session_id=session_id,
        db=mongodb_storage,
        tools=tools,
        instructions=[
            "Use a ferramenta search_user_documents quando a pergunta depender de documentos enviados pelo usuario.",
            "Quando a pergunta for documental, responda apenas com base no contexto retornado pela ferramenta.",
            "Se a ferramenta nao encontrar evidencias, diga que nao encontrou evidencia nos documentos do usuario."
        ],
        markdown=True,
        add_history_to_context=True
    )
