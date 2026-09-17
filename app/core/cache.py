from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)


def inventory_list_key(warehouse_id: int) -> str:
    return f"stockflow:inventory:{warehouse_id}:list"


def inventory_alerts_key(warehouse_id: int) -> str:
    return f"stockflow:inventory:{warehouse_id}:alerts"
