from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.database import get_agent_db, get_db
from src.core.security import (
    decode_jwt_token,
    get_token_from_header,
    extract_user_id_by_token,
)
from src.core.settings import get_settings
from src.schemas.chat import ChatPostRequest, ChatPostResponse
from src.services.chat import (
    UNSUPPORTED_RAG_MODEL_MESSAGE,
    UnsupportedRagModelError,
    chat_once,
    generate_chat_id,
    stream_chat,
)
from src.services.database.chat_db import get_all_id_by_user_id, get_messages_by_chat_id

router = APIRouter(prefix="/chat", tags=["chat"])


@router.websocket(path="/stream")
async def ws_chat(websocket: WebSocket, db: AsyncIOMotorDatabase = Depends(get_db)):
    OPENROUTER_API_KEY = get_settings().OPENROUTER_API_KEY

    model = websocket.query_params.get("model", None)
    use_rag = websocket.query_params.get("use_rag", "true").lower() != "false"

    try:
        rag_limit = int(websocket.query_params.get("rag_limit", "5"))
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if not model:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    await websocket.send_json({"event": "wait_credentials"})
    auth_message = await websocket.receive_json()

    token = auth_message.get("token", None)

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = decode_jwt_token(token)
        user_id = extract_user_id_by_token(payload=payload)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    chat_id = generate_chat_id()

    await websocket.send_json({"event": "accept_connection", "chat_id": chat_id})

    try:
        model_params = await websocket.receive_json()
        await websocket.send_json({"event": "model_params", "params": model_params})

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
                api_key=OPENROUTER_API_KEY,
                rag_db=db,
                use_rag=use_rag,
                rag_limit=rag_limit,
            )

            try:
                async for chunk in async_stream:
                    assistant_full_response += chunk

                    await websocket.send_json({"event": "chunk", "content": chunk})
            except UnsupportedRagModelError:
                assistant_full_response = f"{UNSUPPORTED_RAG_MODEL_MESSAGE}\n\n"

                await websocket.send_json(
                    {"event": "chunk", "content": assistant_full_response}
                )

                fallback_stream = stream_chat(
                    user_id=user_id,
                    chat_id=chat_id,
                    model=model,
                    user_message=user_message,
                    model_params=model_params,
                    api_key=OPENROUTER_API_KEY,
                    rag_db=db,
                    use_rag=False,
                    rag_limit=rag_limit,
                )

                async for chunk in fallback_stream:
                    assistant_full_response += chunk

                    await websocket.send_json({"event": "chunk", "content": chunk})

            await websocket.send_json(
                {"event": "complete_message", "message": assistant_full_response}
            )

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


@router.get(path="/", response_model=list[str])
async def get_all_chat_id(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_agent_db),
):
    return await get_all_id_by_user_id(
        user_id=payload.get("sub"), db=db, limit=limit, skip=skip
    )


@router.get(path="/{id}", response_model=list)
async def get_chat(
    id: str,
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_agent_db),
):
    user_id = payload.get("sub")

    all_messages = await get_messages_by_chat_id(chat_id=id, user_id=user_id, db=db)

    return all_messages


@router.post(path="/", response_model=ChatPostResponse)
async def post_chat(
    chat: ChatPostRequest,
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    OPENROUTER_API_KEY = get_settings().OPENROUTER_API_KEY

    user_id = payload.get("sub")

    chat_id = chat.chat_id

    if not chat_id:
        chat_id = generate_chat_id()

    try:
        agent_response: str = await chat_once(
            user_id=user_id,
            chat_id=chat_id,
            model=chat.model_id,
            user_message=chat.user_message,
            model_params=chat.model_params,
            api_key=OPENROUTER_API_KEY,
            rag_db=db,
            use_rag=chat.use_rag,
            rag_limit=chat.rag_limit,
        )
    except UnsupportedRagModelError:
        fallback_response = await chat_once(
            user_id=user_id,
            chat_id=chat_id,
            model=chat.model_id,
            user_message=chat.user_message,
            model_params=chat.model_params,
            api_key=OPENROUTER_API_KEY,
            rag_db=db,
            use_rag=False,
            rag_limit=chat.rag_limit,
        )
        agent_response = f"{UNSUPPORTED_RAG_MODEL_MESSAGE}\n\n{fallback_response}"

    return ChatPostResponse(chat_id=chat_id, content=agent_response)
