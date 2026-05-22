from pydantic import BaseModel


class EmbeddingsModelsResponse(BaseModel):
    id: str
    name: str
    supported_parameters: list[str] = None


class ReranckingModelsResponse(BaseModel):
    id: str
    name: str
    supported_parameters: list[str] = None


class ChatModelsResponse(BaseModel):
    id: str
    name: str
    supported_parameters: list[str] = None
