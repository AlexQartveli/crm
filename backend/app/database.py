from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

def _database_url() -> str:
    custom = __import__("os").environ.get("KINETIX_DB_PATH")
    if custom:
        path = Path(custom)
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path.as_posix()}"
    return "sqlite:///./kinetix.db"


SQLALCHEMY_DATABASE_URL = _database_url()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_TENANT_COLUMN_TABLES = (
    "users",
    "leads",
    "companies",
    "contacts",
    "deals",
    "deal_products",
    "products",
    "warehouses",
    "stocks",
    "stock_movements",
    "conversations",
    "messages",
    "call_logs",
    "messaging_settings",
    "chat_bots",
    "message_templates",
    "bot_logs",
    "tax_invoices",
    "rsge_settings",
)


def migrate_schema():
    """Добавляет новые колонки в существующую SQLite-базу."""
    from sqlalchemy import inspect

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as conn:
        if "messaging_settings" in table_names:
            existing = {col["name"] for col in inspector.get_columns("messaging_settings")}
            additions = {
                "telegram_bot_token": "VARCHAR(500)",
                "telegram_webhook_secret": "VARCHAR(100)",
                "telegram_connected": "BOOLEAN DEFAULT 0",
            }
            for col, col_type in additions.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE messaging_settings ADD COLUMN {col} {col_type}"))

        if "tenants" not in table_names:
            return

        for table in _TENANT_COLUMN_TABLES:
            if table not in table_names:
                continue
            cols = {col["name"] for col in inspector.get_columns(table)}
            if "tenant_id" not in cols:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN tenant_id INTEGER DEFAULT 1"))
                conn.execute(text(f"UPDATE {table} SET tenant_id = 1 WHERE tenant_id IS NULL"))

        conn.execute(text(
            "UPDATE users SET tenant_id = 1 WHERE tenant_id IS NULL OR tenant_id = 0"
        ))


def ensure_default_tenant(db) -> int:
    from app.models.tenant import Tenant

    tenant = db.query(Tenant).filter(Tenant.slug == "demo").first()
    if tenant:
        return tenant.id

    tenant = Tenant(name="Демо компания", slug="demo", email="demo@kinetix.local")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant.id
