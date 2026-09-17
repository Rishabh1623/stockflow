from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InventoryItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    warehouse_id: int
    sku: str
    quantity_on_hand: int
    reorder_threshold: int
    last_updated: datetime
