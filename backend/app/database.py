from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./kinetix.db"

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


def migrate_schema():
    """Добавляет новые колонки в существующую SQLite-базу."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "messaging_settings" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("messaging_settings")}
    additions = {
        "telegram_bot_token": "VARCHAR(500)",
        "telegram_webhook_secret": "VARCHAR(100)",
        "telegram_connected": "BOOLEAN DEFAULT 0",
    }
    with engine.begin() as conn:
        for col, col_type in additions.items():
            if col not in existing:
                conn.execute(text(f"ALTER TABLE messaging_settings ADD COLUMN {col} {col_type}"))
