from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import app.models  # noqa: F401  registers all models on Base.metadata
from app.api.deps import get_db
from app.core import cache as cache_module
from app.core.config import settings
from app.core.database import Base
from app.main import app
from app.models.inventory_item import InventoryItem
from app.models.warehouse import Warehouse

test_engine = create_async_engine(settings.test_database_url)
test_redis_client = Redis.from_url(settings.test_redis_url, decode_responses=True)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()
    await test_redis_client.aclose()


@pytest.fixture(autouse=True)
async def use_test_redis(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[None, None]:
    """Point the app's cache module at the test Redis DB (index 1 — separate
    from dev's index 0, mirroring the separate stockflow_test Postgres DB) for
    the duration of each test, and flush it so cache state never bleeds
    between tests.

    Patched via the *module*, not the name: app/services/{inventory,orders}.py
    do `from app.core import cache` and call `cache.redis_client`, so
    reassigning the attribute here is visible to them immediately. If they'd
    done `from app.core.cache import redis_client` instead, they'd hold their
    own bound copy of the original client and this patch would silently miss.
    """
    monkeypatch.setattr(cache_module, "redis_client", test_redis_client)
    await test_redis_client.flushdb()
    yield


@pytest.fixture
def test_redis() -> Redis:
    return test_redis_client


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """One connection + outer transaction per test. The app-under-test's
    session is bound to this connection in savepoint mode, so even when
    service-layer code calls session.commit(), it only commits a SAVEPOINT
    — the outer transaction rollback below undoes everything.
    """
    async with test_engine.connect() as connection:
        trans = await connection.begin()
        session = AsyncSession(
            bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def warehouse(db_session: AsyncSession) -> Warehouse:
    wh = Warehouse(name="Test DC", region="us-test")
    db_session.add(wh)
    await db_session.flush()
    return wh


@pytest.fixture
async def inventory_item(db_session: AsyncSession, warehouse: Warehouse) -> InventoryItem:
    item = InventoryItem(
        warehouse_id=warehouse.warehouse_id,
        sku="TEST-SKU",
        quantity_on_hand=10,
        reorder_threshold=5,
    )
    db_session.add(item)
    await db_session.flush()
    return item


@pytest.fixture
async def low_stock_item(db_session: AsyncSession, warehouse: Warehouse) -> InventoryItem:
    item = InventoryItem(
        warehouse_id=warehouse.warehouse_id, sku="LOW-SKU", quantity_on_hand=2, reorder_threshold=10
    )
    db_session.add(item)
    await db_session.flush()
    return item
