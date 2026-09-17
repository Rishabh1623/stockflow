from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    region: Mapped[str] = mapped_column(nullable=False)
