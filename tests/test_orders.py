from httpx import AsyncClient

from app.models.inventory_item import InventoryItem
from app.models.warehouse import Warehouse


async def test_create_order_success(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem
) -> None:
    response = await client.post(
        "/api/v1/orders",
        json={
            "warehouse_id": warehouse.warehouse_id,
            "customer_ref": "cust-1",
            "items": [{"item_id": inventory_item.item_id, "quantity": 2}],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["items"] == [
        {
            "order_item_id": body["items"][0]["order_item_id"],
            "item_id": inventory_item.item_id,
            "quantity": 2,
        }
    ]


async def test_create_order_unknown_warehouse(
    client: AsyncClient, inventory_item: InventoryItem
) -> None:
    response = await client.post(
        "/api/v1/orders",
        json={
            "warehouse_id": 999999,
            "customer_ref": "cust-1",
            "items": [{"item_id": inventory_item.item_id, "quantity": 1}],
        },
    )
    assert response.status_code == 404


async def test_create_order_item_not_in_warehouse(
    client: AsyncClient, db_session, warehouse: Warehouse
) -> None:
    other_warehouse = Warehouse(name="Other DC", region="us-other")
    db_session.add(other_warehouse)
    await db_session.flush()
    other_item = InventoryItem(
        warehouse_id=other_warehouse.warehouse_id,
        sku="OTHER-SKU",
        quantity_on_hand=5,
        reorder_threshold=1,
    )
    db_session.add(other_item)
    await db_session.flush()

    response = await client.post(
        "/api/v1/orders",
        json={
            "warehouse_id": warehouse.warehouse_id,
            "customer_ref": "cust-1",
            "items": [{"item_id": other_item.item_id, "quantity": 1}],
        },
    )
    assert response.status_code == 404


async def test_create_order_rejects_non_positive_quantity(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem
) -> None:
    response = await client.post(
        "/api/v1/orders",
        json={
            "warehouse_id": warehouse.warehouse_id,
            "customer_ref": "cust-1",
            "items": [{"item_id": inventory_item.item_id, "quantity": 0}],
        },
    )
    assert response.status_code == 422


async def test_list_orders_filtered_by_status(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem
) -> None:
    create_body = {
        "warehouse_id": warehouse.warehouse_id,
        "customer_ref": "cust-1",
        "items": [{"item_id": inventory_item.item_id, "quantity": 1}],
    }
    created = (await client.post("/api/v1/orders", json=create_body)).json()

    all_orders = await client.get(f"/api/v1/orders/{warehouse.warehouse_id}")
    assert len(all_orders.json()) == 1

    pending_only = await client.get(
        f"/api/v1/orders/{warehouse.warehouse_id}", params={"status": "pending"}
    )
    assert len(pending_only.json()) == 1

    shipped_only = await client.get(
        f"/api/v1/orders/{warehouse.warehouse_id}", params={"status": "shipped"}
    )
    assert shipped_only.json() == []
    assert created["status"] == "pending"


async def test_fulfill_order_decrements_stock(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem
) -> None:
    starting_qty = inventory_item.quantity_on_hand
    created = (
        await client.post(
            "/api/v1/orders",
            json={
                "warehouse_id": warehouse.warehouse_id,
                "customer_ref": "cust-1",
                "items": [{"item_id": inventory_item.item_id, "quantity": 3}],
            },
        )
    ).json()

    response = await client.patch(
        f"/api/v1/orders/{created['order_id']}/status", json={"status": "fulfilled"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "fulfilled"

    inventory = await client.get(f"/api/v1/inventory/{warehouse.warehouse_id}")
    updated_item = next(i for i in inventory.json() if i["item_id"] == inventory_item.item_id)
    assert updated_item["quantity_on_hand"] == starting_qty - 3


async def test_fulfill_order_insufficient_stock(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem
) -> None:
    # Captured up front: fulfilling triggers a rollback on the shared test session,
    # which expires ORM objects like this fixture — touching it afterward would
    # try to lazily reload it outside of an async-safe context.
    item_id = inventory_item.item_id
    starting_qty = inventory_item.quantity_on_hand
    warehouse_id = warehouse.warehouse_id

    created = (
        await client.post(
            "/api/v1/orders",
            json={
                "warehouse_id": warehouse_id,
                "customer_ref": "cust-1",
                "items": [{"item_id": item_id, "quantity": starting_qty + 1}],
            },
        )
    ).json()

    response = await client.patch(
        f"/api/v1/orders/{created['order_id']}/status", json={"status": "fulfilled"}
    )
    assert response.status_code == 409

    inventory = await client.get(f"/api/v1/inventory/{warehouse_id}")
    updated_item = next(i for i in inventory.json() if i["item_id"] == item_id)
    assert updated_item["quantity_on_hand"] == starting_qty


async def test_invalid_status_transition_rejected(
    client: AsyncClient, warehouse: Warehouse, inventory_item: InventoryItem
) -> None:
    created = (
        await client.post(
            "/api/v1/orders",
            json={
                "warehouse_id": warehouse.warehouse_id,
                "customer_ref": "cust-1",
                "items": [{"item_id": inventory_item.item_id, "quantity": 1}],
            },
        )
    ).json()

    response = await client.patch(
        f"/api/v1/orders/{created['order_id']}/status", json={"status": "shipped"}
    )
    assert response.status_code == 409
