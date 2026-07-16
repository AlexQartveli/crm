from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps.tenant import TenantCtx, get_tenant_ctx, scoped
from app.models.crm import Company, Contact, Deal, DealProduct, Lead
from app.services.messaging_sync import sync_by_contact, sync_by_lead
from app.schemas.crm import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    DealCreate,
    DealProductResponse,
    DealResponse,
    DealUpdate,
    LeadCreate,
    LeadResponse,
    LeadUpdate,
)

router = APIRouter(prefix="/crm", tags=["CRM"])


@router.get("/leads", response_model=list[LeadResponse])
def list_leads(skip: int = 0, limit: int = 100, ctx: TenantCtx = Depends(get_tenant_ctx)):
    return scoped(ctx, Lead).order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/leads", response_model=LeadResponse, status_code=201)
def create_lead(data: LeadCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    lead = Lead(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(lead)
    ctx.db.commit()
    ctx.db.refresh(lead)
    sync_by_lead(ctx.db, lead.id, ctx.tenant_id)
    ctx.db.commit()
    return lead


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    lead = scoped(ctx, Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Лид не найден")
    return lead


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, data: LeadUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    lead = scoped(ctx, Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Лид не найден")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    ctx.db.commit()
    ctx.db.refresh(lead)
    sync_by_lead(ctx.db, lead.id, ctx.tenant_id)
    ctx.db.commit()
    return lead


@router.delete("/leads/{lead_id}", status_code=204)
def delete_lead(lead_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    lead = scoped(ctx, Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Лид не найден")
    ctx.db.delete(lead)
    ctx.db.commit()


@router.get("/companies", response_model=list[CompanyResponse])
def list_companies(skip: int = 0, limit: int = 100, ctx: TenantCtx = Depends(get_tenant_ctx)):
    return scoped(ctx, Company).order_by(Company.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/companies", response_model=CompanyResponse, status_code=201)
def create_company(data: CompanyCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    company = Company(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(company)
    ctx.db.commit()
    ctx.db.refresh(company)
    return company


@router.get("/companies/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    company = scoped(ctx, Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    return company


@router.patch("/companies/{company_id}", response_model=CompanyResponse)
def update_company(company_id: int, data: CompanyUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    company = scoped(ctx, Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    ctx.db.commit()
    ctx.db.refresh(company)
    return company


@router.delete("/companies/{company_id}", status_code=204)
def delete_company(company_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    company = scoped(ctx, Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    ctx.db.delete(company)
    ctx.db.commit()


@router.get("/contacts", response_model=list[ContactResponse])
def list_contacts(skip: int = 0, limit: int = 100, ctx: TenantCtx = Depends(get_tenant_ctx)):
    return scoped(ctx, Contact).order_by(Contact.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/contacts", response_model=ContactResponse, status_code=201)
def create_contact(data: ContactCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    contact = Contact(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(contact)
    ctx.db.commit()
    ctx.db.refresh(contact)
    sync_by_contact(ctx.db, contact.id, ctx.tenant_id)
    ctx.db.commit()
    return contact


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    contact = scoped(ctx, Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return contact


@router.patch("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, data: ContactUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    contact = scoped(ctx, Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
    ctx.db.commit()
    ctx.db.refresh(contact)
    sync_by_contact(ctx.db, contact.id, ctx.tenant_id)
    ctx.db.commit()
    return contact


@router.delete("/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    contact = scoped(ctx, Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    ctx.db.delete(contact)
    ctx.db.commit()


def _deal_to_response(deal: Deal) -> DealResponse:
    products = [
        DealProductResponse(
            id=dp.id,
            product_id=dp.product_id,
            quantity=dp.quantity,
            price=dp.price,
            product_name=dp.product.name if dp.product else None,
        )
        for dp in deal.products
    ]
    return DealResponse(
        id=deal.id,
        title=deal.title,
        stage=deal.stage,
        amount=deal.amount,
        contact_id=deal.contact_id,
        company_id=deal.company_id,
        comment=deal.comment,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        products=products,
        contact_name=deal.contact.name if deal.contact else None,
        company_name=deal.company.name if deal.company else None,
    )


@router.get("/deals", response_model=list[DealResponse])
def list_deals(skip: int = 0, limit: int = 100, ctx: TenantCtx = Depends(get_tenant_ctx)):
    deals = scoped(ctx, Deal).order_by(Deal.updated_at.desc()).offset(skip).limit(limit).all()
    return [_deal_to_response(d) for d in deals]


@router.post("/deals", response_model=DealResponse, status_code=201)
def create_deal(data: DealCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    deal_data = data.model_dump(exclude={"products"})
    deal = Deal(tenant_id=ctx.tenant_id, **deal_data)
    ctx.db.add(deal)
    ctx.db.flush()

    total = 0.0
    for item in data.products:
        dp = DealProduct(tenant_id=ctx.tenant_id, deal_id=deal.id, **item.model_dump())
        ctx.db.add(dp)
        total += item.quantity * item.price

    if total > 0:
        deal.amount = total

    ctx.db.commit()
    ctx.db.refresh(deal)
    return _deal_to_response(deal)


@router.get("/deals/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    deal = scoped(ctx, Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    return _deal_to_response(deal)


@router.patch("/deals/{deal_id}", response_model=DealResponse)
def update_deal(deal_id: int, data: DealUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    deal = scoped(ctx, Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(deal, key, value)
    ctx.db.commit()
    ctx.db.refresh(deal)
    return _deal_to_response(deal)


@router.delete("/deals/{deal_id}", status_code=204)
def delete_deal(deal_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    deal = scoped(ctx, Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    ctx.db.delete(deal)
    ctx.db.commit()
