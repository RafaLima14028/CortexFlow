from typing import Any

from pydantic import BaseModel, Field, field_validator


class ChatMessageResponse(BaseModel):
    index: int
    content: str
    role: str


class ChatResponse(BaseModel):
    messages: list[ChatMessageResponse]
    has_more: bool


class ChatPostRequest(BaseModel):
    model_id: str
    user_message: str
    model_params: dict[str, Any] = Field(default_factory=dict)
    chat_id: str | None = None
    use_rag: bool = True
    rag_limit: int = Field(default=5, ge=1, le=20)

    @field_validator("user_message")
    @classmethod
    def validate_user_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("User message is empty")

        return value


class ChatPostResponse(BaseModel):
    chat_id: str
    content: str
