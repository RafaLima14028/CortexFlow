from typing import Any
from pydantic import BaseModel


class EmbeddingResult(BaseModel):
    embeddings: list[float]
    dimensions: int
    chunk: str
    chunk_id: str
    meta_data: dict[str, Any] = None
