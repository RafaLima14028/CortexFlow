from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional, Literal
from fastapi import HTTPException, status


class ChunkingConfig(BaseModel):
    chunk_size: Optional[int] = None
    overlap: Optional[int] = None
    similarity_threshold: Optional[float] = None
    separators: Optional[list[str]] = None


class ChunkingRequest(BaseModel):
    strategy: Literal[
        "fixed",
        "semantic",
        "recursive",
        "markdown"
    ] = "fixed"
    config: ChunkingConfig = Field(
        default_factory=ChunkingConfig
    )

    @model_validator(mode='after')
    def validate_strategy_parameters(self) -> 'ChunkingRequest':
        strategy = self.strategy
        conf = self.config

        requirements = {
            "fixed": ["chunk_size", "overlap"],
            "recursive": ["chunk_size", "overlap"],
            "semantic": ["similarity_threshold"],
            "markdown": ["chunk_size"],
        }

        required_fields = requirements.get(strategy, [])
        missing = [
            field for field in required_fields if getattr(
                conf,
                field
            ) is None
        ]

        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "InvalidConfiguration",
                    "strategy": strategy,
                    "missing_fields": missing,
                    "message": f"The strategy {strategy} need the fields: {', '.join(missing)}"
                }
            )

        return self


class ChunkingResponse(BaseModel):
    chunk: str
    id: str
    meta_data: dict[str, Any] = None


class EmbeddingRequest(BaseModel):
    model_id: str
    model_params: dict[str, Any] = {}


class EmbeddingResponse(BaseModel):
    vector: list[float]


class DocumentRequest(BaseModel):
    embedding: EmbeddingRequest
    chunking: ChunkingRequest


class DocumentResponse(BaseModel):
    id: str
    filename: str
    model_id: str


class DocumentResponseInternal(BaseModel):
    id: str
    filename: str
    model_id: str
    collection: str


class ChunkEmbeddingItem(BaseModel):
    chunk: ChunkingResponse
    embeddings: EmbeddingResponse


class DocumentEmbeddingChunkResponse(BaseModel):
    infos: DocumentResponse
    datas: list[ChunkEmbeddingItem]
