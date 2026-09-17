"""Seed sample warehouses + inventory items for local dev/demo.

Run with: uv run python -m scripts.seed

There's no POST /warehouses or POST /inventory endpoint in Stage 1's spec
(only orders create anything), so this script is the only way to get
reference data to build orders against locally.
"""

import asyncio

from sqlalchemy import select

from app.core.database import async_session_factory
from app.models.inventory_item import InventoryItem
from app.models.warehouse import Warehouse


async def seed() -> None:
    async with async_session_factory() as session:
        existing = await session.execute(select(Warehouse))
        if existing.scalars().first() is not None:
            print("Warehouses already exist, skipping seed.")
            return

        east = Warehouse(name="East Coast DC", region="us-east")
        west = Warehouse(name="West Coast DC", region="us-west")
        session.add_all([east, west])
        await session.flush()  # assign warehouse_id values

        session.add_all(
            [
                InventoryItem(
                    warehouse_id=east.warehouse_id,
                    sku="WIDGET-001",
                    quantity_on_hand=150,
                    reorder_threshold=50,
                ),
                InventoryItem(
                    warehouse_id=east.warehouse_id,
                    sku="GADGET-002",
                    quantity_on_hand=12,
                    reorder_threshold=25,  # below threshold: shows up in alerts
                ),
                InventoryItem(
                    warehouse_id=west.warehouse_id,
                    sku="WIDGET-001",
                    quantity_on_hand=80,
                    reorder_threshold=30,
                ),
                InventoryItem(
                    warehouse_id=west.warehouse_id,
                    sku="GIZMO-003",
                    quantity_on_hand=5,
                    reorder_threshold=20,  # below threshold: shows up in alerts
                ),
            ]
        )
        await session.commit()
        print(
            f"Seeded warehouses {east.warehouse_id} and {west.warehouse_id} with inventory items."
        )


if __name__ == "__main__":
    asyncio.run(seed())
