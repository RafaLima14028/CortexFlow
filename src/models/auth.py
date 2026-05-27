from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)


class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: EmailStr
    hashed_password: str
    created_at: datetime

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}
