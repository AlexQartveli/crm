from sqlalchemy.orm import Session

from app.models.warehouse import MovementType, Stock, StockMovement
from app.schemas.warehouse import StockMovementCreate


def get_or_create_stock(db: Session, product_id: int, warehouse_id: int) -> Stock:
    stock = (
        db.query(Stock)
        .filter(Stock.product_id == product_id, Stock.warehouse_id == warehouse_id)
        .first()
    )
    if not stock:
        stock = Stock(product_id=product_id, warehouse_id=warehouse_id, quantity=0.0)
        db.add(stock)
        db.flush()
    return stock


def apply_movement(db: Session, data: StockMovementCreate) -> StockMovement:
    movement = StockMovement(**data.model_dump())
    db.add(movement)

    if data.movement_type == MovementType.RECEIPT.value:
        stock = get_or_create_stock(db, data.product_id, data.warehouse_id)
        stock.quantity += data.quantity

    elif data.movement_type == MovementType.EXPENSE.value:
        stock = get_or_create_stock(db, data.product_id, data.warehouse_id)
        if stock.quantity - stock.reserved < data.quantity:
            raise ValueError("Недостаточно товара на складе")
        stock.quantity -= data.quantity

    elif data.movement_type == MovementType.TRANSFER.value:
        from_stock = get_or_create_stock(db, data.product_id, data.warehouse_id)
        if from_stock.quantity - from_stock.reserved < data.quantity:
            raise ValueError("Недостаточно товара для перемещения")
        from_stock.quantity -= data.quantity
        to_stock = get_or_create_stock(db, data.product_id, data.to_warehouse_id)
        to_stock.quantity += data.quantity

    elif data.movement_type == MovementType.ADJUSTMENT.value:
        stock = get_or_create_stock(db, data.product_id, data.warehouse_id)
        stock.quantity = data.quantity

    return movement
