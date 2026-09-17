import json

from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import cache as cache_module
from app.core.config import settings
from app.models.inventory_item import InventoryItem
from app.models.warehouse import Warehouse


async def test_inventory_read_populates_cache_with_ttl(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem, test_redis: Redis
) -> None:
    await client.get(f"/api/v1/inventory/{warehouse.warehouse_id}")

    key = cache_module.inventory_list_key(warehouse.warehouse_id)
    raw = await test_redis.get(key)
    assert raw is not None
    assert json.loads(raw)[0]["sku"] == inventory_item.sku

    ttl = await test_redis.ttl(key)
    assert 0 < ttl <= settings.inventory_cache_ttl_seconds


async def test_cached_read_serves_stale_data_until_invalidated(
    client: AsyncClient,
    db_session: AsyncSession,
    warehouse: Warehouse,
    inventory_item: InventoryItem,
) -> None:
    # First read populates the cache.
    first = await client.get(f"/api/v1/inventory/{warehouse.warehouse_id}")
    original_qty = first.json()[0]["quantity_on_hand"]

    # Mutate the DB directly, bypassing the API (and therefore bypassing
    # cache invalidation) entirely — simulates any write path that isn't
    # the one place (order fulfillment) that knows to invalidate.
    inventory_item.quantity_on_hand = 999
    await db_session.flush()

    # If caching weren't actually happening, this would show 999. It doesn't
    # — proving the second call is served from cache, not a fresh DB query.
    second = await client.get(f"/api/v1/inventory/{warehouse.warehouse_id}")
    assert second.json()[0]["quantity_on_hand"] == original_qty


async def test_fulfillment_invalidates_both_inventory_caches(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem
) -> None:
    # inventory_item fixture: quantity_on_hand=10, reorder_threshold=5 — starts healthy.
    warehouse_id = warehouse.warehouse_id
    item_id = inventory_item.item_id
    sku = inventory_item.sku

    # Prime both caches before the mutation.
    list_before = await client.get(f"/api/v1/inventory/{warehouse_id}")
    alerts_before = await client.get(f"/api/v1/inventory/{warehouse_id}/alerts")
    assert list_before.json()[0]["quantity_on_hand"] == 10
    assert alerts_before.json() == []

    created = (
        await client.post(
            "/api/v1/orders",
            json={
                "warehouse_id": warehouse_id,
                "customer_ref": "cust-1",
                "items": [{"item_id": item_id, "quantity": 6}],  # 10 - 6 = 4, below threshold of 5
            },
        )
    ).json()
    await client.patch(f"/api/v1/orders/{created['order_id']}/status", json={"status": "fulfilled"})

    list_after = await client.get(f"/api/v1/inventory/{warehouse_id}")
    alerts_after = await client.get(f"/api/v1/inventory/{warehouse_id}/alerts")

    updated_item = next(i for i in list_after.json() if i["item_id"] == item_id)
    assert updated_item["quantity_on_hand"] == 4

    alert_skus = [i["sku"] for i in alerts_after.json()]
    assert alert_skus == [sku]
