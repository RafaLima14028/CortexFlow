from typing import Any, AsyncGenerator
from agno.run.agent import RunOutput
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

from src.agents.conversation_agent import get_conversation_agent


UNSUPPORTED_RAG_MODEL_MESSAGE = (
    "Este modelo nao tem suporte a consulta dos arquivos enviados. "
    "Vou desativar a busca nos documentos e continuar como um chat comum."
)


class UnsupportedRagModelError(Exception):
    pass


def is_unsupported_rag_model_error(error: Exception) -> bool:
    return is_unsupported_rag_model_message(str(error))


def is_unsupported_rag_model_message(message: str) -> bool:
    if not message:
        return False

    return (
        "No endpoints found that support tool use" in message
        and "search_user_documents" in message
    )


def generate_chat_id() -> str:
    return str(uuid.uuid4())


async def stream_chat(
    user_id: str,
    chat_id: str,
    model: str,
    user_message: str,
    model_params: dict[str, Any],
    api_key: str,
    rag_db: AsyncIOMotorDatabase | None = None,
    use_rag: bool = True,
    rag_limit: int = 5
) -> AsyncGenerator[str, None]:
    agent = get_conversation_agent(
        api_key=api_key,
        user_id=user_id,
        session_id=chat_id,
        model_id=model,
        model_params=model_params,
        rag_db=rag_db,
        use_rag=use_rag,
        rag_limit=rag_limit
    )

    response_stream = agent.arun(
        input=user_message,
        stream=True
    )

    try:
        async for chunk in response_stream:
            if chunk and chunk.content:
                if is_unsupported_rag_model_message(str(chunk.content)):
                    raise UnsupportedRagModelError(
                        UNSUPPORTED_RAG_MODEL_MESSAGE
                    )

                yield chunk.content
    except Exception as error:
        if is_unsupported_rag_model_error(error):
            raise UnsupportedRagModelError(
                UNSUPPORTED_RAG_MODEL_MESSAGE
            ) from error

        raise


async def chat_once(
    user_id: str,
    chat_id: str,
    model: str,
    user_message: str,
    model_params: dict[str, Any],
    api_key: str,
    rag_db: AsyncIOMotorDatabase | None = None,
    use_rag: bool = True,
    rag_limit: int = 5
) -> str:
    agent = get_conversation_agent(
        api_key=api_key,
        user_id=user_id,
        session_id=chat_id,
        model_id=model,
        model_params=model_params,
        rag_db=rag_db,
        use_rag=use_rag,
        rag_limit=rag_limit
    )

    try:
        response: RunOutput = await agent.arun(
            input=user_message,
            stream=False
        )
    except Exception as error:
        if is_unsupported_rag_model_error(error):
            raise UnsupportedRagModelError(
                UNSUPPORTED_RAG_MODEL_MESSAGE
            ) from error

        raise

    content = str(response.content)

    if is_unsupported_rag_model_message(content):
        raise UnsupportedRagModelError(
            UNSUPPORTED_RAG_MODEL_MESSAGE
        )

    return content
