from httpx import AsyncClient

from app.models.warehouse import Warehouse


async def test_list_warehouses(client: AsyncClient, warehouse: Warehouse) -> None:
    response = await client.get("/api/v1/warehouses")
    assert response.status_code == 200
    body = response.json()
    assert any(w["warehouse_id"] == warehouse.warehouse_id for w in body)


async def test_list_warehouses_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/warehouses")
    assert response.status_code == 200
    assert response.json() == []
