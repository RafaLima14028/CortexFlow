from pydantic import BaseModel


class AvailableEmbeddingModelInDB(BaseModel):
    id: str
    name: str
    supported_parameters: list[str] = None
