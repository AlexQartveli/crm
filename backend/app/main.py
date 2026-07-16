from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func

from app.database import Base, SessionLocal, engine, migrate_schema
from app.deps.tenant import TenantCtx, get_tenant_ctx
from app.models.crm import Company, Contact, Deal, Lead
from app.models.tenant import Tenant
from app.models.messaging import Conversation
from app.models.warehouse import Product, Stock
from app.routers import accounting, auth, automations, crm, messaging, tenant, warehouse
from app.seed_crm_template import seed_crm_template
from app.seed_demo_tenants import seed_demo_tenants
from app.seed_users import seed_users
from app.middleware.auth import AuthMiddleware

Base.metadata.create_all(bind=engine)
migrate_schema()

app = FastAPI(
    title="Kinetix",
    description="CRM + Склад — Kinetix",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.include_router(auth.router, prefix="/api")
app.include_router(tenant.router, prefix="/api")
app.include_router(crm.router, prefix="/api")
app.include_router(warehouse.router, prefix="/api")
app.include_router(accounting.router, prefix="/api")
app.include_router(messaging.router, prefix="/api")
app.include_router(automations.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        tenant_id = seed_users(db)
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        seed_crm_template(db, tenant_id, tenant.crm_type if tenant else "general")
        seed_demo_tenants(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/dashboard")
def dashboard(ctx: TenantCtx = Depends(get_tenant_ctx)):
    tid = ctx.tenant_id
    leads_count = (
        ctx.db.query(func.count(Lead.id)).filter(Lead.tenant_id == tid).scalar() or 0
    )
    deals_count = (
        ctx.db.query(func.count(Deal.id)).filter(Deal.tenant_id == tid).scalar() or 0
    )
    contacts_count = (
        ctx.db.query(func.count(Contact.id)).filter(Contact.tenant_id == tid).scalar() or 0
    )
    companies_count = (
        ctx.db.query(func.count(Company.id)).filter(Company.tenant_id == tid).scalar() or 0
    )
    products_count = (
        ctx.db.query(func.count(Product.id)).filter(Product.tenant_id == tid).scalar() or 0
    )
    total_stock = (
        ctx.db.query(func.sum(Stock.quantity)).filter(Stock.tenant_id == tid).scalar() or 0
    )

    deals_by_stage = (
        ctx.db.query(Deal.stage, func.count(Deal.id))
        .filter(Deal.tenant_id == tid)
        .group_by(Deal.stage)
        .all()
    )

    won_amount = (
        ctx.db.query(func.sum(Deal.amount))
        .filter(Deal.tenant_id == tid, Deal.stage == "won")
        .scalar()
        or 0
    )

    pipeline_amount = (
        ctx.db.query(func.sum(Deal.amount))
        .filter(Deal.tenant_id == tid, Deal.stage.notin_(["won", "lost"]))
        .scalar()
        or 0
    )

    unread_messages = (
        ctx.db.query(func.coalesce(func.sum(Conversation.unread_count), 0))
        .filter(Conversation.tenant_id == tid)
        .scalar()
        or 0
    )
    conversations_count = (
        ctx.db.query(func.count(Conversation.id))
        .filter(Conversation.tenant_id == tid)
        .scalar()
        or 0
    )

    return {
        "leads": leads_count,
        "deals": deals_count,
        "contacts": contacts_count,
        "companies": companies_count,
        "products": products_count,
        "total_stock": total_stock,
        "won_amount": won_amount,
        "pipeline_amount": pipeline_amount,
        "deals_by_stage": {stage: count for stage, count in deals_by_stage},
        "unread_messages": unread_messages,
        "conversations": conversations_count,
    }


def _mount_frontend(app: FastAPI) -> None:
    import os

    static_dir = os.environ.get("KINETIX_STATIC_DIR")
    if not static_dir or not Path(static_dir).is_dir():
        return

    assets_dir = Path(static_dir) / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    def spa_root():
        return FileResponse(Path(static_dir) / "index.html")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        file_path = Path(static_dir) / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(Path(static_dir) / "index.html")


_mount_frontend(app)
