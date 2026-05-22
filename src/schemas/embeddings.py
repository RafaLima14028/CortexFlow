from pydantic import BaseModel
from typing import Any


class EmbeddingsResults(BaseModel):
    embeddings: list[float]
    dimensions: int
    chunk: str
    chunk_id: str
    meta_data: dict[str, Any] = None
