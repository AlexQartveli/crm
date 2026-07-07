from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.accounting import InvoiceStatus, RsgeSettings, TaxInvoice
from app.models.crm import Company, Deal
from app.schemas.accounting import (
    RsgeAuthRequest,
    RsgeAuthResponse,
    RsgeSettingsCreate,
    RsgeSettingsResponse,
    SyncInvoiceRequest,
    TaxInvoiceCreate,
    TaxInvoiceResponse,
    VatCheckRequest,
    VatCheckResponse,
)
from app.services import rsge

router = APIRouter(prefix="/accounting", tags=["Бухгалтерия"])


def _invoice_response(inv: TaxInvoice, db: Session) -> TaxInvoiceResponse:
    deal = db.query(Deal).filter(Deal.id == inv.deal_id).first() if inv.deal_id else None
    company = db.query(Company).filter(Company.id == inv.company_id).first() if inv.company_id else None
    return TaxInvoiceResponse(
        id=inv.id,
        number=inv.number,
        deal_id=inv.deal_id,
        company_id=inv.company_id,
        tin_seller=inv.tin_seller,
        tin_buyer=inv.tin_buyer,
        buyer_name=inv.buyer_name,
        amount=inv.amount,
        vat_rate=inv.vat_rate,
        vat_amount=inv.vat_amount,
        total_amount=inv.total_amount,
        status=inv.status,
        rsge_invoice_id=inv.rsge_invoice_id,
        rsge_transaction_id=inv.rsge_transaction_id,
        description=inv.description,
        operation_date=inv.operation_date,
        created_at=inv.created_at,
        synced_at=inv.synced_at,
        deal_title=deal.title if deal else None,
        company_name=company.name if company else None,
    )


@router.get("/invoices", response_model=list[TaxInvoiceResponse])
def list_invoices(db: Session = Depends(get_db)):
    invoices = db.query(TaxInvoice).order_by(TaxInvoice.created_at.desc()).all()
    return [_invoice_response(inv, db) for inv in invoices]


@router.post("/invoices", response_model=TaxInvoiceResponse, status_code=201)
def create_invoice(data: TaxInvoiceCreate, db: Session = Depends(get_db)):
    vat, total = rsge.calc_vat(data.amount, data.vat_rate)
    count = db.query(TaxInvoice).count()
    inv = TaxInvoice(
        number=f"INV-{datetime.now().year}-{count + 1:04d}",
        deal_id=data.deal_id,
        company_id=data.company_id,
        tin_seller=data.tin_seller,
        tin_buyer=data.tin_buyer,
        buyer_name=data.buyer_name,
        amount=data.amount,
        vat_rate=data.vat_rate,
        vat_amount=vat,
        total_amount=total,
        description=data.description,
        operation_date=datetime.utcnow(),
        status=InvoiceStatus.DRAFT.value,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return _invoice_response(inv, db)


@router.post("/invoices/{invoice_id}/sync", response_model=TaxInvoiceResponse)
async def sync_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(TaxInvoice).filter(TaxInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Счёт не найден")

    try:
        result = await rsge.save_invoice_to_rsge({
            "tin_seller": inv.tin_seller,
            "tin_buyer": inv.tin_buyer,
            "operation_date": inv.operation_date.strftime("%d-%m-%Y %H:%M:%S") if inv.operation_date else None,
            "goods": [{"name": inv.description or "Услуга", "quantity": 1, "unit_price": inv.amount}],
        })
        inv.rsge_transaction_id = result.get("transaction_id")
        inv.rsge_invoice_id = result.get("invoice_id")
        inv.status = InvoiceStatus.SENT.value
        inv.synced_at = datetime.utcnow()
        db.commit()
        db.refresh(inv)
        return _invoice_response(inv, db)
    except rsge.RsgeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/invoices/{invoice_id}/activate", response_model=TaxInvoiceResponse)
async def activate_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(TaxInvoice).filter(TaxInvoice.id == invoice_id).first()
    if not inv or not inv.rsge_invoice_id:
        raise HTTPException(status_code=404, detail="Счёт не найден или не синхронизирован")

    try:
        ok = await rsge.activate_invoice_rsge(inv.rsge_invoice_id)
        if ok:
            inv.status = InvoiceStatus.ACTIVE.value
            db.commit()
            db.refresh(inv)
        return _invoice_response(inv, db)
    except rsge.RsgeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/settings", response_model=RsgeSettingsResponse | None)
def get_settings(db: Session = Depends(get_db)):
    return db.query(RsgeSettings).first()


@router.post("/settings", response_model=RsgeSettingsResponse)
def save_settings(data: RsgeSettingsCreate, db: Session = Depends(get_db)):
    settings = db.query(RsgeSettings).first()
    if not settings:
        settings = RsgeSettings(
            company_tin=data.company_tin,
            username=data.username,
            password_enc=data.password,
        )
        db.add(settings)
    else:
        settings.company_tin = data.company_tin
        settings.username = data.username
        settings.password_enc = data.password
    db.commit()
    db.refresh(settings)
    return RsgeSettingsResponse(
        id=settings.id,
        company_tin=settings.company_tin,
        username=settings.username,
        is_connected=settings.is_connected,
        last_sync=settings.last_sync,
    )


@router.post("/rsge/auth", response_model=RsgeAuthResponse)
async def rsge_auth(data: RsgeAuthRequest, db: Session = Depends(get_db)):
    try:
        result = await rsge.authenticate(
            data.username, data.password,
            pin=data.pin, pin_token=data.pin_token,
        )
        if result.get("needs_pin"):
            return RsgeAuthResponse(success=False, needs_pin=True, pin_token=result.get("pin_token"))
        settings = db.query(RsgeSettings).first()
        if settings:
            settings.is_connected = True
            settings.last_sync = datetime.utcnow()
            db.commit()
        return RsgeAuthResponse(success=True, message="Подключено к RS.ge")
    except rsge.RsgeError as e:
        return RsgeAuthResponse(success=False, message=str(e))


@router.post("/rsge/check-vat", response_model=VatCheckResponse)
async def check_vat(data: VatCheckRequest):
    try:
        result = await rsge.check_vat_payer(data.tin, data.date)
        return VatCheckResponse(**result)
    except rsge.RsgeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
