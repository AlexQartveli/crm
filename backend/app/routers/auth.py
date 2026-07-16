from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.crm_config import config_to_api, get_crm_config
from app.core.crm_types import CRM_TYPES
from app.core.permissions import ALL_ROLES, ROLE_LABELS, get_role_permissions
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.deps.auth import get_current_user, user_permissions
from app.deps.tenant import TenantCtx, get_tenant_ctx, scoped
from app.models.tenant import Tenant, normalize_slug
from app.models.user import User
from app.schemas.auth import (
    AuthUserResponse,
    ChangePasswordRequest,
    CrmTypeResponse,
    DemoAccountResponse,
    CrmServiceResponse,
    LoginRequest,
    ProfileUpdate,
    RegisterRequest,
    RoleInfo,
    TenantResponse,
    TenantUpdate,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.tenant_provision import provision_tenant
from app.seed_demo_tenants import list_demo_accounts

router = APIRouter(prefix="/auth", tags=["Auth"])


def _tenant_response(tenant: Tenant) -> TenantResponse:
    return TenantResponse.model_validate(tenant)


def _auth_user(user: User, tenant: Tenant) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        created_at=user.created_at,
        permissions=user_permissions(user),
        tenant=_tenant_response(tenant),
    )


@router.get("/crm-types", response_model=list[CrmTypeResponse])
def list_crm_types():
    result = []
    for t in CRM_TYPES.values():
        cfg = get_crm_config(t.id)
        result.append(CrmTypeResponse(
            id=t.id,
            label_ru=t.label_ru,
            label_en=t.label_en,
            label_ka=t.label_ka,
            desc_ru=t.desc_ru,
            desc_en=t.desc_en,
            desc_ka=t.desc_ka,
            icon=t.icon,
            features=list(cfg.modules),
            modules=list(cfg.modules),
            services=[
                CrmServiceResponse(
                    id=s.id,
                    label_ru=s.label.ru,
                    label_en=s.label.en,
                    label_ka=s.label.ka,
                )
                for s in cfg.services
            ],
        ))
    return result


@router.get("/demo-accounts", response_model=list[DemoAccountResponse])
def demo_accounts():
    return [DemoAccountResponse(**a) for a in list_demo_accounts()]


@router.get("/crm-config")
def get_crm_config(ctx: TenantCtx = Depends(get_tenant_ctx)):
    return config_to_api(ctx.tenant.crm_type or "general")


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        tenant, admin = provision_tenant(
            db,
            company_name=data.company_name,
            slug=data.company_slug,
            admin_username=data.admin_username,
            admin_password=data.admin_password,
            admin_full_name=data.admin_full_name,
            admin_email=data.admin_email,
            company_email=data.company_email,
            company_phone=data.company_phone,
            crm_type=data.crm_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    token = create_access_token(
        user_id=admin.id, username=admin.username, role=admin.role, tenant_id=tenant.id,
    )
    return TokenResponse(access_token=token, user=_auth_user(admin, tenant))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    slug = normalize_slug(data.company_slug)
    tenant = db.query(Tenant).filter(Tenant.slug == slug, Tenant.is_active.is_(True)).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Компания не найдена")

    user = (
        db.query(User)
        .filter(User.tenant_id == tenant.id, User.username == data.username.strip())
        .first()
    )
    if not user or not user.is_active or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token(
        user_id=user.id, username=user.username, role=user.role, tenant_id=tenant.id,
    )
    return TokenResponse(access_token=token, user=_auth_user(user, tenant))


@router.get("/me", response_model=AuthUserResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    return _auth_user(user, tenant)


@router.patch("/profile", response_model=AuthUserResponse)
def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.full_name is not None:
        user.full_name = data.full_name.strip()
    if data.email is not None:
        user.email = data.email
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    return _auth_user(user, tenant)


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")
    user.hashed_password = hash_password(data.new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}


@router.post("/logout")
def logout():
    return {"ok": True}


@router.get("/roles", response_model=list[RoleInfo])
def list_roles(_user: User = Depends(get_current_user)):
    return [
        RoleInfo(
            id=role,
            label_ru=ROLE_LABELS[role]["ru"],
            label_en=ROLE_LABELS[role]["en"],
            label_ka=ROLE_LABELS[role]["ka"],
            permissions=sorted(get_role_permissions(role)),
        )
        for role in ALL_ROLES
    ]


@router.get("/users", response_model=list[UserResponse])
def list_users(ctx: TenantCtx = Depends(get_tenant_ctx)):
    return scoped(ctx, User).order_by(User.full_name.asc()).all()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    if data.role not in ALL_ROLES:
        raise HTTPException(status_code=400, detail="Неизвестная роль")
    if scoped(ctx, User).filter(User.username == data.username.strip()).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user = User(
        tenant_id=ctx.tenant_id,
        username=data.username.strip(),
        email=data.email,
        full_name=data.full_name.strip(),
        role=data.role,
        hashed_password=hash_password(data.password),
    )
    ctx.db.add(user)
    ctx.db.commit()
    ctx.db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    user = scoped(ctx, User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if data.role is not None:
        if data.role not in ALL_ROLES:
            raise HTTPException(status_code=400, detail="Неизвестная роль")
        user.role = data.role
    if data.full_name is not None:
        user.full_name = data.full_name.strip()
    if data.email is not None:
        user.email = data.email
    if data.is_active is not None:
        if user.id == ctx.user.id and not data.is_active:
            raise HTTPException(status_code=400, detail="Нельзя деактивировать себя")
        user.is_active = data.is_active
    if data.password:
        user.hashed_password = hash_password(data.password)

    user.updated_at = datetime.utcnow()
    ctx.db.commit()
    ctx.db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    user = scoped(ctx, User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id == ctx.user.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить себя")
    ctx.db.delete(user)
    ctx.db.commit()
