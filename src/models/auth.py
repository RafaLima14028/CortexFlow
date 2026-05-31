from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)


class UserInDB(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: EmailStr
    hashed_password: str
    created_at: datetime

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}
