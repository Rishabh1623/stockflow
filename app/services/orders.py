from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import cache
from app.models.inventory_item import InventoryItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.warehouse import Warehouse
from app.schemas.order import OrderCreate
from app.services.exceptions import InsufficientStockError, InvalidTransitionError, NotFoundError

# Legal next states for each current order status. Anything not listed here
# (including no-ops and backwards moves) is rejected as an invalid transition.
ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.FULFILLED, OrderStatus.CANCELLED},
    OrderStatus.FULFILLED: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED: set(),
    OrderStatus.CANCELLED: set(),
}


async def _get_warehouse_or_404(session: AsyncSession, warehouse_id: int) -> Warehouse:
    warehouse = await session.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise NotFoundError(f"warehouse {warehouse_id} not found")
    return warehouse


async def create_order(session: AsyncSession, data: OrderCreate) -> Order:
    await _get_warehouse_or_404(session, data.warehouse_id)

    item_ids = [line.item_id for line in data.items]
    result = await session.execute(select(InventoryItem).where(InventoryItem.item_id.in_(item_ids)))
    items_by_id = {item.item_id: item for item in result.scalars().all()}

    missing = set(item_ids) - items_by_id.keys()
    if missing:
        raise NotFoundError(f"inventory item(s) not found: {sorted(missing)}")

    wrong_warehouse = [
        item_id for item_id, item in items_by_id.items() if item.warehouse_id != data.warehouse_id
    ]
    if wrong_warehouse:
        raise NotFoundError(
            f"inventory item(s) do not belong to warehouse {data.warehouse_id}: "
            f"{sorted(wrong_warehouse)}"
        )

    order = Order(
        warehouse_id=data.warehouse_id,
        customer_ref=data.customer_ref,
        status=OrderStatus.PENDING,
        items=[OrderItem(item_id=line.item_id, quantity=line.quantity) for line in data.items],
    )
    session.add(order)
    await session.commit()
    return await get_order(session, order.order_id)


async def list_orders(
    session: AsyncSession, warehouse_id: int, status: OrderStatus | None = None
) -> list[Order]:
    await _get_warehouse_or_404(session, warehouse_id)

    stmt = (
        select(Order)
        .where(Order.warehouse_id == warehouse_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    if status is not None:
        stmt = stmt.where(Order.status == status)

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_order(session: AsyncSession, order_id: int) -> Order:
    stmt = select(Order).where(Order.order_id == order_id).options(selectinload(Order.items))
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundError(f"order {order_id} not found")
    return order


async def update_order_status(
    session: AsyncSession, order_id: int, new_status: OrderStatus
) -> Order:
    order = await get_order(session, order_id)

    if new_status not in ALLOWED_TRANSITIONS[order.status]:
        raise InvalidTransitionError(f"cannot move order from {order.status} to {new_status}")

    decremented_stock = order.status == OrderStatus.PENDING and new_status == OrderStatus.FULFILLED
    if decremented_stock:
        await _decrement_stock_for_order(session, order)

    order.status = new_status
    await session.commit()

    if decremented_stock:
        # Invalidate only after commit — the decrement isn't durable/visible to
        # other transactions until now, so invalidating any earlier risks a
        # concurrent request repopulating the cache with pre-decrement data.
        await cache.redis_client.delete(
            cache.inventory_list_key(order.warehouse_id),
            cache.inventory_alerts_key(order.warehouse_id),
        )

    return await get_order(session, order_id)


async def _decrement_stock_for_order(session: AsyncSession, order: Order) -> None:
    """Conditionally decrement stock per line item so two concurrent
    fulfillments can't overdraw the same SKU. Raises before anything is
    committed if any line item has insufficient stock, so the whole
    transition is rolled back atomically.
    """
    for line in order.items:
        result = await session.execute(
            update(InventoryItem)
            .where(
                InventoryItem.item_id == line.item_id,
                InventoryItem.quantity_on_hand >= line.quantity,
            )
            .values(quantity_on_hand=InventoryItem.quantity_on_hand - line.quantity)
        )
        if result.rowcount == 0:
            item_id, quantity = line.item_id, line.quantity
            await session.rollback()
            raise InsufficientStockError(f"insufficient stock for item {item_id} (need {quantity})")
