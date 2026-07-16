from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str
    role: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AuthUserResponse(UserResponse):
    permissions: list[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=4, max_length=100)
    full_name: str = Field(min_length=1, max_length=120)
    email: str | None = None
    role: str = "sales"


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=4, max_length=100)


class RoleInfo(BaseModel):
    id: str
    label_ru: str
    label_en: str
    label_ka: str
    permissions: list[str]
