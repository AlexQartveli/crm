"""Демо-пользователи для каждой роли."""

from sqlalchemy.orm import Session

from app.core.permissions import ALL_ROLES
from app.core.security import hash_password
from app.models.user import User

DEFAULT_USERS = [
    ("admin", "admin", "Администратор", "admin"),
    ("director", "director", "Руководитель", "director"),
    ("sales", "sales", "Менеджер по продажам", "sales"),
    ("operator", "operator", "Оператор поддержки", "operator"),
    ("warehouse", "warehouse", "Кладовщик", "warehouse"),
    ("accountant", "accountant", "Бухгалтер", "accountant"),
]


def seed_users(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    for username, password, full_name, role in DEFAULT_USERS:
        if role not in ALL_ROLES:
            continue
        db.add(User(
            username=username,
            full_name=full_name,
            role=role,
            hashed_password=hash_password(f"{password}123"),
            email=f"{username}@kinetix.local",
        ))
    db.commit()
