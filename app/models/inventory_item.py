from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.warehouse import Warehouse


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    __table_args__ = (UniqueConstraint("warehouse_id", "sku", name="uq_inventory_warehouse_sku"),)

    item_id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.warehouse_id"), nullable=False)
    sku: Mapped[str] = mapped_column(nullable=False)
    quantity_on_hand: Mapped[int] = mapped_column(nullable=False, default=0)
    reorder_threshold: Mapped[int] = mapped_column(nullable=False, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    warehouse: Mapped[Warehouse] = relationship()
