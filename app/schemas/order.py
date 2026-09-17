from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    warehouse_id: int
    customer_ref: str
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_item_id: int
    item_id: int
    quantity: int


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    warehouse_id: int
    customer_ref: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemRead]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
