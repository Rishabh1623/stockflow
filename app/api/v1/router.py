from fastapi import APIRouter

from app.api.v1 import inventory, orders, warehouses

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(orders.router)
api_router.include_router(inventory.router)
api_router.include_router(warehouses.router)
