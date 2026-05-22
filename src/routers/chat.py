from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    status,
    Depends,
    Query
)
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.security import (
    decode_jwt_token,
    get_token_from_header
)
from src.core.settings import get_settings
from src.core.database import get_agent_db
from src.services.database.chat_db import (
    get_messages_by_chat_id,
    get_all_id_by_user_id
)
from src.schemas.chat import (
    ChatPostRequest,
    ChatPostResponse
)
from src.services.chat import (
    stream_chat,
    sync_chat,
    generate_chat_id
)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.websocket(
    path="/stream"
)
async def ws_chat(
    websocket: WebSocket
):
    OPENROUTER_API_KEY = get_settings().OPENROUTER_API_KEY

    token = websocket.query_params.get("token", None)
    model = websocket.query_params.get("model", None)

    if not token or not model:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")
    except Exception:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION
        )
        return

    chat_id = generate_chat_id()

    await websocket.accept()
    await websocket.send_json({
        "event": "accept_connection",
        "chat_id": chat_id
    })

    try:
        model_params = await websocket.receive_json()
        await websocket.send_json({
            "event": "Model params received",
            "params": model_params
        })

        while True:
            msg = await websocket.receive_json()
            user_message = msg.get("user_message")

            if not user_message:
                continue

            assistant_full_response = ""

            async_stream = stream_chat(
                user_id=user_id,
                chat_id=chat_id,
                model=model,
                user_message=user_message,
                model_params=model_params,
                api_key=OPENROUTER_API_KEY
            )

            async for chunk in async_stream:
                assistant_full_response += chunk

                await websocket.send_json({
                    "event": "chunk",
                    "content": chunk
                })

            await websocket.send_json({
                "event": "complete_message",
                "message": assistant_full_response
            })

            await websocket.send_json({"event": "message_end"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.get(
    path="/",
    response_model=list[str]
)
async def get_all_chat_id(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_agent_db)
):
    return await get_all_id_by_user_id(
        user_id=payload.get("sub"),
        db=db,
        limit=limit,
        skip=skip
    )


@router.get(
    path="/{id}",
    response_model=list
)
async def get_chat(
    id: str,
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_agent_db)
):
    user_id = payload.get("sub")

    all_messages = await get_messages_by_chat_id(
        chat_id=id,
        user_id=user_id,
        db=db
    )

    return all_messages


@router.post(
    path="/",
    response_model=ChatPostResponse
)
async def post_chat(
    chat: ChatPostRequest,
    payload: dict = Depends(get_token_from_header)
):
    OPENROUTER_API_KEY = get_settings().OPENROUTER_API_KEY

    user_id = payload.get("sub")

    chat_id = chat.chat_id

    if not chat_id:
        chat_id = generate_chat_id()

    agent_response: str = sync_chat(
        user_id=user_id,
        chat_id=chat_id,
        model=chat.model_id,
        user_message=chat.user_message,
        model_params=chat.model_params,
        api_key=OPENROUTER_API_KEY
    )

    return ChatPostResponse(
        chat_id=chat_id,
        content=agent_response
    )
