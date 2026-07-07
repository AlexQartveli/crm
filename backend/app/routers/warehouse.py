from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.warehouse import MovementType, Product, Stock, StockMovement, Warehouse
from app.schemas.warehouse import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    StockMovementCreate,
    StockMovementResponse,
    StockResponse,
    WarehouseCreate,
    WarehouseResponse,
    WarehouseUpdate,
)
from app.services.stock import apply_movement, get_or_create_stock

router = APIRouter(prefix="/warehouse", tags=["Склад"])


@router.get("/products", response_model=list[ProductResponse])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.name).offset(skip).limit(limit).all()
    result = []
    for p in products:
        total = sum(s.quantity for s in p.stocks)
        result.append(
            ProductResponse(
                id=p.id,
                name=p.name,
                sku=p.sku,
                unit=p.unit,
                price=p.price,
                description=p.description,
                created_at=p.created_at,
                total_stock=total,
            )
        )
    return result


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    if data.sku:
        existing = db.query(Product).filter(Product.sku == data.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="Товар с таким артикулом уже существует")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse(
        id=product.id,
        name=product.name,
        sku=product.sku,
        unit=product.unit,
        price=product.price,
        description=product.description,
        created_at=product.created_at,
        total_stock=0.0,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    total = sum(s.quantity for s in product.stocks)
    return ProductResponse(
        id=product.id,
        name=product.name,
        sku=product.sku,
        unit=product.unit,
        price=product.price,
        description=product.description,
        created_at=product.created_at,
        total_stock=total,
    )


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    total = sum(s.quantity for s in product.stocks)
    return ProductResponse(
        id=product.id,
        name=product.name,
        sku=product.sku,
        unit=product.unit,
        price=product.price,
        description=product.description,
        created_at=product.created_at,
        total_stock=total,
    )


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    db.delete(product)
    db.commit()


@router.get("/warehouses", response_model=list[WarehouseResponse])
def list_warehouses(db: Session = Depends(get_db)):
    return db.query(Warehouse).order_by(Warehouse.name).all()


@router.post("/warehouses", response_model=WarehouseResponse, status_code=201)
def create_warehouse(data: WarehouseCreate, db: Session = Depends(get_db)):
    if data.is_default:
        db.query(Warehouse).update({Warehouse.is_default: False})
    warehouse = Warehouse(**data.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.patch("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: int, data: WarehouseUpdate, db: Session = Depends(get_db)
):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Склад не найден")
    if data.is_default:
        db.query(Warehouse).update({Warehouse.is_default: False})
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(warehouse, key, value)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.get("/stocks", response_model=list[StockResponse])
def list_stocks(
    warehouse_id: int | None = None,
    product_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Stock)
    if warehouse_id:
        query = query.filter(Stock.warehouse_id == warehouse_id)
    if product_id:
        query = query.filter(Stock.product_id == product_id)
    stocks = query.all()
    return [
        StockResponse(
            id=s.id,
            product_id=s.product_id,
            warehouse_id=s.warehouse_id,
            quantity=s.quantity,
            reserved=s.reserved,
            product_name=s.product.name if s.product else None,
            warehouse_name=s.warehouse.name if s.warehouse else None,
            available=s.quantity - s.reserved,
        )
        for s in stocks
    ]


@router.get("/movements", response_model=list[StockMovementResponse])
def list_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movements = (
        db.query(StockMovement)
        .order_by(StockMovement.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        StockMovementResponse(
            id=m.id,
            product_id=m.product_id,
            warehouse_id=m.warehouse_id,
            movement_type=m.movement_type,
            quantity=m.quantity,
            to_warehouse_id=m.to_warehouse_id,
            deal_id=m.deal_id,
            comment=m.comment,
            created_at=m.created_at,
            product_name=m.product.name if m.product else None,
            warehouse_name=m.warehouse.name if m.warehouse else None,
        )
        for m in movements
    ]


@router.post("/movements", response_model=StockMovementResponse, status_code=201)
def create_movement(data: StockMovementCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    warehouse = db.query(Warehouse).filter(Warehouse.id == data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Склад не найден")

    if data.movement_type not in [t.value for t in MovementType]:
        raise HTTPException(status_code=400, detail="Неверный тип движения")

    if data.movement_type == MovementType.TRANSFER.value and not data.to_warehouse_id:
        raise HTTPException(status_code=400, detail="Укажите склад назначения для перемещения")

    try:
        movement = apply_movement(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    db.commit()
    db.refresh(movement)
    return StockMovementResponse(
        id=movement.id,
        product_id=movement.product_id,
        warehouse_id=movement.warehouse_id,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        to_warehouse_id=movement.to_warehouse_id,
        deal_id=movement.deal_id,
        comment=movement.comment,
        created_at=movement.created_at,
        product_name=product.name,
        warehouse_name=warehouse.name,
    )
