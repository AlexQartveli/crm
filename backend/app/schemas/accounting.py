from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaxInvoiceBase(BaseModel):
    deal_id: int | None = None
    company_id: int | None = None
    tin_seller: str
    tin_buyer: str
    buyer_name: str | None = None
    amount: float = 0.0
    vat_rate: float = 18.0
    description: str | None = None


class TaxInvoiceCreate(TaxInvoiceBase):
    pass


class TaxInvoiceResponse(TaxInvoiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str | None = None
    vat_amount: float
    total_amount: float
    status: str
    rsge_invoice_id: int | None = None
    rsge_transaction_id: str | None = None
    operation_date: datetime | None = None
    created_at: datetime
    synced_at: datetime | None = None
    deal_title: str | None = None
    company_name: str | None = None


class RsgeSettingsBase(BaseModel):
    company_tin: str
    username: str


class RsgeSettingsCreate(RsgeSettingsBase):
    password: str


class RsgeSettingsResponse(RsgeSettingsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_connected: bool
    last_sync: datetime | None = None


class RsgeAuthRequest(BaseModel):
    username: str
    password: str
    pin: str | None = None
    pin_token: str | None = None


class RsgeAuthResponse(BaseModel):
    success: bool
    needs_pin: bool = False
    pin_token: str | None = None
    message: str | None = None


class VatCheckRequest(BaseModel):
    tin: str
    date: str | None = None


class VatCheckResponse(BaseModel):
    tin: str
    is_vat_payer: bool
    org_name: str | None = None


class SyncInvoiceRequest(BaseModel):
    invoice_id: int
