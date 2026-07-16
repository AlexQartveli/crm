"""Демо-пользователи для каждой роли."""

from sqlalchemy.orm import Session

from app.core.permissions import ALL_ROLES
from app.core.security import hash_password
from app.database import ensure_default_tenant
from app.models.accounting import RsgeSettings
from app.models.messaging import MessagingSettings
from app.models.user import User

DEFAULT_USERS = [
    ("admin", "admin", "Администратор", "admin"),
    ("director", "director", "Руководитель", "director"),
    ("sales", "sales", "Менеджер по продажам", "sales"),
    ("operator", "operator", "Оператор поддержки", "operator"),
    ("warehouse", "warehouse", "Кладовщик", "warehouse"),
    ("accountant", "accountant", "Бухгалтер", "accountant"),
]


def seed_users(db: Session) -> int:
    tenant_id = ensure_default_tenant(db)

    if not db.query(MessagingSettings).filter(MessagingSettings.tenant_id == tenant_id).first():
        db.add(MessagingSettings(tenant_id=tenant_id))
    if not db.query(RsgeSettings).filter(RsgeSettings.tenant_id == tenant_id).first():
        db.add(RsgeSettings(tenant_id=tenant_id, company_tin="", username=""))
    db.commit()

    if db.query(User).filter(User.tenant_id == tenant_id).count() > 0:
        return tenant_id

    for username, password, full_name, role in DEFAULT_USERS:
        if role not in ALL_ROLES:
            continue
        db.add(User(
            tenant_id=tenant_id,
            username=username,
            full_name=full_name,
            role=role,
            hashed_password=hash_password(f"{password}123"),
            email=f"{username}@kinetix.local",
        ))
    db.commit()
    return tenant_id
