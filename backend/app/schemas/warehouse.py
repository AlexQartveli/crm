from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    sku: str | None = None
    unit: str = "шт"
    price: float = 0.0
    description: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    unit: str | None = None
    price: float | None = None
    description: str | None = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    total_stock: float = 0.0


class WarehouseBase(BaseModel):
    name: str
    address: str | None = None
    is_default: bool = False


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    is_default: bool | None = None


class WarehouseResponse(WarehouseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class StockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    warehouse_id: int
    quantity: float
    reserved: float
    product_name: str | None = None
    warehouse_name: str | None = None
    available: float = 0.0


class StockMovementCreate(BaseModel):
    product_id: int
    warehouse_id: int
    movement_type: str
    quantity: float
    to_warehouse_id: int | None = None
    deal_id: int | None = None
    comment: str | None = None


class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    warehouse_id: int
    movement_type: str
    quantity: float
    to_warehouse_id: int | None = None
    deal_id: int | None = None
    comment: str | None = None
    created_at: datetime
    product_name: str | None = None
    warehouse_name: str | None = None
