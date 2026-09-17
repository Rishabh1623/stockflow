import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import cache
from app.core.config import settings
from app.models.inventory_item import InventoryItem
from app.models.warehouse import Warehouse
from app.schemas.inventory import InventoryItemRead
from app.services.exceptions import NotFoundError


async def _get_warehouse_or_404(session: AsyncSession, warehouse_id: int) -> Warehouse:
    warehouse = await session.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise NotFoundError(f"warehouse {warehouse_id} not found")
    return warehouse


async def _cache_items(cache_key: str, items: list[InventoryItemRead]) -> None:
    payload = json.dumps([item.model_dump(mode="json") for item in items])
    await cache.redis_client.set(cache_key, payload, ex=settings.inventory_cache_ttl_seconds)


async def list_inventory(session: AsyncSession, warehouse_id: int) -> list[InventoryItemRead]:
    cache_key = cache.inventory_list_key(warehouse_id)
    cached = await cache.redis_client.get(cache_key)
    if cached is not None:
        return [InventoryItemRead.model_validate(row) for row in json.loads(cached)]

    await _get_warehouse_or_404(session, warehouse_id)
    result = await session.execute(
        select(InventoryItem).where(InventoryItem.warehouse_id == warehouse_id)
    )
    items = [InventoryItemRead.model_validate(item) for item in result.scalars().all()]
    await _cache_items(cache_key, items)
    return items


async def list_low_stock_alerts(
    session: AsyncSession, warehouse_id: int
) -> list[InventoryItemRead]:
    cache_key = cache.inventory_alerts_key(warehouse_id)
    cached = await cache.redis_client.get(cache_key)
    if cached is not None:
        return [InventoryItemRead.model_validate(row) for row in json.loads(cached)]

    await _get_warehouse_or_404(session, warehouse_id)
    result = await session.execute(
        select(InventoryItem).where(
            InventoryItem.warehouse_id == warehouse_id,
            InventoryItem.quantity_on_hand < InventoryItem.reorder_threshold,
        )
    )
    items = [InventoryItemRead.model_validate(item) for item in result.scalars().all()]
    await _cache_items(cache_key, items)
    return items
