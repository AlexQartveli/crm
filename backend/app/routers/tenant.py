from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps.tenant import TenantCtx, get_tenant_ctx
from app.models.tenant import Tenant
from app.schemas.auth import TenantResponse, TenantUpdate

router = APIRouter(prefix="/tenant", tags=["Tenant"])


@router.get("/me", response_model=TenantResponse)
def get_my_tenant(ctx: TenantCtx = Depends(get_tenant_ctx)):
    tenant = ctx.db.query(Tenant).filter(Tenant.id == ctx.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    return tenant


@router.patch("/me", response_model=TenantResponse)
def update_my_tenant(data: TenantUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    if ctx.user.role not in ("admin", "director"):
        raise HTTPException(status_code=403, detail="Только администратор может менять данные компании")

    tenant = ctx.db.query(Tenant).filter(Tenant.id == ctx.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Компания не найдена")

    for field in ("name", "email", "phone", "address"):
        value = getattr(data, field)
        if value is not None:
            setattr(tenant, field, value.strip() if isinstance(value, str) else value)
    tenant.updated_at = datetime.utcnow()
    ctx.db.commit()
    ctx.db.refresh(tenant)
    return tenant
