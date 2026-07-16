from fastapi import APIRouter, Depends, HTTPException

from app.deps.tenant import TenantCtx, get_tenant_ctx, scoped
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
from app.services.stock import apply_movement

router = APIRouter(prefix="/warehouse", tags=["Склад"])


@router.get("/products", response_model=list[ProductResponse])
def list_products(skip: int = 0, limit: int = 100, ctx: TenantCtx = Depends(get_tenant_ctx)):
    products = scoped(ctx, Product).order_by(Product.name).offset(skip).limit(limit).all()
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
def create_product(data: ProductCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    if data.sku:
        existing = scoped(ctx, Product).filter(Product.sku == data.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="Товар с таким артикулом уже существует")
    product = Product(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(product)
    ctx.db.commit()
    ctx.db.refresh(product)
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
def get_product(product_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    product = scoped(ctx, Product).filter(Product.id == product_id).first()
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
def update_product(product_id: int, data: ProductUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    product = scoped(ctx, Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    ctx.db.commit()
    ctx.db.refresh(product)
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
def delete_product(product_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    product = scoped(ctx, Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    ctx.db.delete(product)
    ctx.db.commit()


@router.get("/warehouses", response_model=list[WarehouseResponse])
def list_warehouses(ctx: TenantCtx = Depends(get_tenant_ctx)):
    return scoped(ctx, Warehouse).order_by(Warehouse.name).all()


@router.post("/warehouses", response_model=WarehouseResponse, status_code=201)
def create_warehouse(data: WarehouseCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    if data.is_default:
        scoped(ctx, Warehouse).update({Warehouse.is_default: False})
    warehouse = Warehouse(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(warehouse)
    ctx.db.commit()
    ctx.db.refresh(warehouse)
    return warehouse


@router.patch("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: int, data: WarehouseUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)
):
    warehouse = scoped(ctx, Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Склад не найден")
    if data.is_default:
        scoped(ctx, Warehouse).update({Warehouse.is_default: False})
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(warehouse, key, value)
    ctx.db.commit()
    ctx.db.refresh(warehouse)
    return warehouse


@router.get("/stocks", response_model=list[StockResponse])
def list_stocks(
    warehouse_id: int | None = None,
    product_id: int | None = None,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    query = scoped(ctx, Stock)
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
def list_movements(skip: int = 0, limit: int = 100, ctx: TenantCtx = Depends(get_tenant_ctx)):
    movements = (
        scoped(ctx, StockMovement)
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
def create_movement(data: StockMovementCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    product = scoped(ctx, Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    warehouse = scoped(ctx, Warehouse).filter(Warehouse.id == data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Склад не найден")

    if data.movement_type not in [t.value for t in MovementType]:
        raise HTTPException(status_code=400, detail="Неверный тип движения")

    if data.movement_type == MovementType.TRANSFER.value and not data.to_warehouse_id:
        raise HTTPException(status_code=400, detail="Укажите склад назначения для перемещения")

    if data.to_warehouse_id:
        to_wh = scoped(ctx, Warehouse).filter(Warehouse.id == data.to_warehouse_id).first()
        if not to_wh:
            raise HTTPException(status_code=404, detail="Склад назначения не найден")

    try:
        movement = apply_movement(ctx.db, data, ctx.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    ctx.db.commit()
    ctx.db.refresh(movement)
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
