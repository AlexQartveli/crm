from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    REFUSED = "refused"


class TaxInvoice(Base):
    __tablename__ = "tax_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    deal_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("deals.id"), nullable=True)
    company_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True)
    tin_seller: Mapped[str] = mapped_column(String(20))
    tin_buyer: Mapped[str] = mapped_column(String(20))
    buyer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    vat_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, default=18.0)
    status: Mapped[str] = mapped_column(String(50), default=InvoiceStatus.DRAFT.value)
    rsge_invoice_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rsge_transaction_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    operation_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class RsgeSettings(Base):
    __tablename__ = "rsge_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_tin: Mapped[str] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(100))
    password_enc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_connected: Mapped[bool] = mapped_column(default=False)
    last_sync: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
