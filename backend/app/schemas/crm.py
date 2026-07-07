from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeadBase(BaseModel):
    title: str
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    source: str | None = None
    status: str = "new"
    amount: float = 0.0
    comment: str | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    title: str | None = None
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    source: str | None = None
    status: str | None = None
    amount: float | None = None
    comment: str | None = None


class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CompanyBase(BaseModel):
    name: str
    inn: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    comment: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    inn: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    comment: str | None = None


class CompanyResponse(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ContactBase(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    position: str | None = None
    company_id: int | None = None
    comment: str | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    position: str | None = None
    company_id: int | None = None
    comment: str | None = None


class ContactResponse(ContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class DealProductBase(BaseModel):
    product_id: int
    quantity: float = 1.0
    price: float = 0.0


class DealProductCreate(DealProductBase):
    pass


class DealProductResponse(DealProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_name: str | None = None


class DealBase(BaseModel):
    title: str
    stage: str = "new"
    amount: float = 0.0
    contact_id: int | None = None
    company_id: int | None = None
    comment: str | None = None


class DealCreate(DealBase):
    products: list[DealProductCreate] = []


class DealUpdate(BaseModel):
    title: str | None = None
    stage: str | None = None
    amount: float | None = None
    contact_id: int | None = None
    company_id: int | None = None
    comment: str | None = None


class DealResponse(DealBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    products: list[DealProductResponse] = []
    contact_name: str | None = None
    company_name: str | None = None
