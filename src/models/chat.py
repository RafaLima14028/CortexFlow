from pydantic import BaseModel


class ChatMessageInDB(BaseModel):
    index: int
    content: str
    role: str
