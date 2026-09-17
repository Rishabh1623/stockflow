from fastapi import APIRouter, Depends
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.order import OrderStatus
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate
from app.services import orders as orders_service

router = APIRouter(tags=["orders"])


@router.post("/orders", response_model=OrderRead, status_code=http_status.HTTP_201_CREATED)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)) -> OrderRead:
    order = await orders_service.create_order(db, data)
    return OrderRead.model_validate(order)


@router.get("/orders/{warehouse_id}", response_model=list[OrderRead])
async def list_orders(
    warehouse_id: int, status: OrderStatus | None = None, db: AsyncSession = Depends(get_db)
) -> list[OrderRead]:
    orders = await orders_service.list_orders(db, warehouse_id, status)
    return [OrderRead.model_validate(order) for order in orders]


@router.patch("/orders/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    order_id: int, data: OrderStatusUpdate, db: AsyncSession = Depends(get_db)
) -> OrderRead:
    order = await orders_service.update_order_status(db, order_id, data.status)
    return OrderRead.model_validate(order)
