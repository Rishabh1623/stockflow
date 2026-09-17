import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.inventory_item import InventoryItem
from app.models.warehouse import Warehouse


class OrderStatus(enum.StrEnum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.warehouse_id"), nullable=False)
    customer_ref: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=20), nullable=False, default=OrderStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    warehouse: Mapped[Warehouse] = relationship()
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.item_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")
    item: Mapped[InventoryItem] = relationship()
