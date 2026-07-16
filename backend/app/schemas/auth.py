from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    company_slug: str = Field(min_length=2, max_length=50)
    username: str
    password: str


class RegisterRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    company_slug: str = Field(min_length=2, max_length=50)
    admin_username: str = Field(min_length=2, max_length=50)
    admin_password: str = Field(min_length=4, max_length=100)
    admin_full_name: str = Field(min_length=1, max_length=120)
    admin_email: str | None = None
    company_email: str | None = None
    company_phone: str | None = None


class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TenantUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=4, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str
    role: str
    is_active: bool
    tenant_id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AuthUserResponse(UserResponse):
    permissions: list[str]
    tenant: TenantResponse


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
