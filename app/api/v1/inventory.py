from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.inventory import InventoryItemRead
from app.services import inventory as inventory_service

router = APIRouter(tags=["inventory"])


@router.get("/inventory/{warehouse_id}", response_model=list[InventoryItemRead])
async def list_inventory(
    warehouse_id: int, db: AsyncSession = Depends(get_db)
) -> list[InventoryItemRead]:
    return await inventory_service.list_inventory(db, warehouse_id)


@router.get("/inventory/{warehouse_id}/alerts", response_model=list[InventoryItemRead])
async def list_alerts(
    warehouse_id: int, db: AsyncSession = Depends(get_db)
) -> list[InventoryItemRead]:
    return await inventory_service.list_low_stock_alerts(db, warehouse_id)
