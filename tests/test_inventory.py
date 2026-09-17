from httpx import AsyncClient

from app.models.inventory_item import InventoryItem
from app.models.warehouse import Warehouse


async def test_list_inventory(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem
) -> None:
    response = await client.get(f"/api/v1/inventory/{warehouse.warehouse_id}")
    assert response.status_code == 200
    skus = [item["sku"] for item in response.json()]
    assert skus == [inventory_item.sku]


async def test_list_inventory_unknown_warehouse(client: AsyncClient) -> None:
    response = await client.get("/api/v1/inventory/999999")
    assert response.status_code == 404


async def test_alerts_returns_only_low_stock(
    client: AsyncClient,
    warehouse: Warehouse,
    inventory_item: InventoryItem,
    low_stock_item: InventoryItem,
) -> None:
    response = await client.get(f"/api/v1/inventory/{warehouse.warehouse_id}/alerts")
    assert response.status_code == 200
    skus = [item["sku"] for item in response.json()]
    assert skus == [low_stock_item.sku]
