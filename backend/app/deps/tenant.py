from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User


@dataclass
class TenantCtx:
    db: Session
    tenant_id: int
    user: User


def get_tenant_ctx(request: Request, db: Session = Depends(get_db)) -> TenantCtx:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    return TenantCtx(db=db, tenant_id=user.tenant_id, user=user)


def scoped(ctx: TenantCtx, model):
    return ctx.db.query(model).filter(model.tenant_id == ctx.tenant_id)


def get_scoped(ctx: TenantCtx, model, item_id: int):
    return scoped(ctx, model).filter(model.id == item_id).first()
