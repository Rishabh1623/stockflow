from pydantic import BaseModel, ConfigDict


class WarehouseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    warehouse_id: int
    name: str
    region: str
