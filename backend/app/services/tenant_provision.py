"""Создание новой компании (tenant) с администратором и базовыми настройками."""

from sqlalchemy.orm import Session

from app.core.crm_types import DEFAULT_CRM_TYPE, is_valid_crm_type
from app.core.security import hash_password
from app.models.accounting import RsgeSettings
from app.models.messaging import MessagingSettings
from app.models.tenant import Tenant, normalize_slug
from app.models.user import User
from app.seed_crm_template import seed_crm_template


def slug_available(db: Session, slug: str) -> bool:
    return db.query(Tenant).filter(Tenant.slug == slug).first() is None


def provision_tenant(
    db: Session,
    *,
    company_name: str,
    slug: str,
    admin_username: str,
    admin_password: str,
    admin_full_name: str,
    admin_email: str | None = None,
    company_email: str | None = None,
    company_phone: str | None = None,
    crm_type: str = DEFAULT_CRM_TYPE,
) -> tuple[Tenant, User]:
    normalized = normalize_slug(slug)
    if not normalized:
        raise ValueError("Некорректный код компании")
    if not slug_available(db, normalized):
        raise ValueError("Компания с таким кодом уже существует")

    crm = crm_type if is_valid_crm_type(crm_type) else DEFAULT_CRM_TYPE

    tenant = Tenant(
        name=company_name.strip(),
        slug=normalized,
        email=company_email,
        phone=company_phone,
        crm_type=crm,
    )
    db.add(tenant)
    db.flush()

    admin = User(
        tenant_id=tenant.id,
        username=admin_username.strip(),
        full_name=admin_full_name.strip(),
        email=admin_email,
        role="admin",
        hashed_password=hash_password(admin_password),
    )
    db.add(admin)
    db.add(MessagingSettings(tenant_id=tenant.id))
    db.add(RsgeSettings(tenant_id=tenant.id, company_tin="", username=""))

    db.commit()
    db.refresh(tenant)
    db.refresh(admin)

    seed_crm_template(db, tenant.id, crm)
    return tenant, admin
