from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token_type: str = "Bearer"
    access_token: str


class RefreshRequest(BaseModel):
    ...


class RefreshResponse(BaseModel):
    ...
