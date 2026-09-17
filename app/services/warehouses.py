from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseRead


async def list_warehouses(session: AsyncSession) -> list[WarehouseRead]:
    result = await session.execute(select(Warehouse).order_by(Warehouse.name))
    return [WarehouseRead.model_validate(w) for w in result.scalars().all()]
