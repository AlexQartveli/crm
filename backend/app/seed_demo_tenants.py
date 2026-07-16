"""Демо-компании для каждого типа CRM — быстрый просмотр без регистрации."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.crm_types import ALL_CRM_TYPE_IDS, CRM_TYPES, DEFAULT_CRM_TYPE, get_crm_type
from app.core.security import hash_password
from app.models.accounting import RsgeSettings
from app.models.messaging import MessagingSettings
from app.models.tenant import Tenant
from app.models.user import User
from app.seed_crm_template import seed_crm_template
from app.services.tenant_provision import provision_tenant

DEMO_USERNAME = "admin"
DEMO_PASSWORD = "demo123"


def demo_slug(crm_type: str) -> str:
    if crm_type == DEFAULT_CRM_TYPE:
        return "demo"
    return f"demo-{crm_type}"


def seed_demo_tenants(db: Session) -> None:
    """Создаёт демо-tenant для каждого типа CRM с готовыми данными."""
    for crm_type in ALL_CRM_TYPE_IDS:
        slug = demo_slug(crm_type)
        info = get_crm_type(crm_type)
        tenant = db.query(Tenant).filter(Tenant.slug == slug).first()

        if tenant is None:
            if slug == "demo":
                continue
            try:
                provision_tenant(
                    db,
                    company_name=f"Демо — {info.label_ru}",
                    slug=slug,
                    admin_username=DEMO_USERNAME,
                    admin_password=DEMO_PASSWORD,
                    admin_full_name="Демо администратор",
                    admin_email=f"{slug}@kinetix.local",
                    company_email=f"{slug}@kinetix.local",
                    crm_type=crm_type,
                )
            except ValueError:
                tenant = db.query(Tenant).filter(Tenant.slug == slug).first()
                if tenant is None:
                    continue
            continue

        if tenant.crm_type != crm_type:
            tenant.crm_type = crm_type
            db.commit()

        _ensure_tenant_settings(db, tenant.id)
        _ensure_demo_admin(db, tenant.id, slug)
        seed_crm_template(db, tenant.id, crm_type)


def _ensure_tenant_settings(db: Session, tenant_id: int) -> None:
    if not db.query(MessagingSettings).filter(MessagingSettings.tenant_id == tenant_id).first():
        db.add(MessagingSettings(tenant_id=tenant_id))
    if not db.query(RsgeSettings).filter(RsgeSettings.tenant_id == tenant_id).first():
        db.add(RsgeSettings(tenant_id=tenant_id, company_tin="", username=""))
    db.commit()


def _ensure_demo_admin(db: Session, tenant_id: int, slug: str) -> None:
    admin = (
        db.query(User)
        .filter(User.tenant_id == tenant_id, User.username == DEMO_USERNAME)
        .first()
    )
    if admin:
        return

    db.add(User(
        tenant_id=tenant_id,
        username=DEMO_USERNAME,
        full_name="Демо администратор",
        role="admin",
        hashed_password=hash_password(DEMO_PASSWORD),
        email=f"{slug}@kinetix.local",
    ))
    db.commit()


def list_demo_accounts() -> list[dict]:
    """Публичный список демо-входов для API."""
    accounts = []
    for crm_type in ALL_CRM_TYPE_IDS:
        info = CRM_TYPES[crm_type]
        slug = demo_slug(crm_type)
        password = "admin123" if slug == "demo" else DEMO_PASSWORD
        accounts.append({
            "crm_type": crm_type,
            "slug": slug,
            "label_ru": info.label_ru,
            "label_en": info.label_en,
            "label_ka": info.label_ka,
            "desc_ru": info.desc_ru,
            "desc_en": info.desc_en,
            "desc_ka": info.desc_ka,
            "icon": info.icon,
            "username": DEMO_USERNAME,
            "password": password,
        })
    return accounts
