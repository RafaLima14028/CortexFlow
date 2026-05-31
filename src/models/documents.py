from pydantic import BaseModel
from typing import Any


class DocumentInDB(BaseModel):
    id: str
    user_id: str
    filename: str
    model_id: str
    embedding_model_params: dict[str, Any]
    collection: str


class DocumentChunk(BaseModel):
    id: str
    chunk: str
    meta_data: dict[str, Any] = None


class EmbeddingChunkInDB(BaseModel):
    chunk: DocumentChunk
    embeddings: list[float]

