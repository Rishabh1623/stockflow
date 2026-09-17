from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.warehouse import WarehouseRead
from app.services import warehouses as warehouses_service

router = APIRouter(tags=["warehouses"])


@router.get("/warehouses", response_model=list[WarehouseRead])
async def list_warehouses(db: AsyncSession = Depends(get_db)) -> list[WarehouseRead]:
    return await warehouses_service.list_warehouses(db)
