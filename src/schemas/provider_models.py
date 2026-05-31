from pydantic import BaseModel


class EmbeddingModelResponse(BaseModel):
    id: str
    name: str
    supported_parameters: list[str] = None


class RerankingModelResponse(BaseModel):
    id: str
    name: str
    supported_parameters: list[str] = None


class ChatModelResponse(BaseModel):
    id: str
    name: str
    supported_parameters: list[str] = None
