from typing import Any, AsyncGenerator
from agno.run.agent import RunOutput
import uuid

from src.agents.conversation_agent import get_conversation_agent


def generate_chat_id() -> str:
    return str(uuid.uuid4())


async def stream_chat(
    user_id: str,
    chat_id: str,
    model: str,
    user_message: str,
    model_params: dict[str, Any],
    api_key: str
) -> AsyncGenerator[str, None]:
    agent = get_conversation_agent(
        api_key=api_key,
        user_id=user_id,
        session_id=chat_id,
        model_id=model,
        model_params=model_params
    )

    response_stream = agent.arun(
        input=user_message,
        stream=True
    )

    async for chunk in response_stream:
        if chunk and chunk.content:
            yield chunk.content


def sync_chat(
    user_id: str,
    chat_id: str,
    model: str,
    user_message: str,
    model_params: dict[str, Any],
    api_key: str
) -> str:
    agent = get_conversation_agent(
        api_key=api_key,
        user_id=user_id,
        session_id=chat_id,
        model_id=model,
        model_params=model_params
    )

    response: RunOutput = agent.run(
        input=user_message,
        stream=False
    )

    return str(response.content)
