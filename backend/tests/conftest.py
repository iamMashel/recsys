import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db

ASYNC_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/recsys_test"
SYNC_DB_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/recsys_test"


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once synchronously before any async tests run."""
    engine = create_engine(SYNC_DB_URL)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest_asyncio.fixture
async def client(create_tables):
    """Fresh async engine + HTTP client per test — no shared event loop state."""
    engine = create_async_engine(ASYNC_DB_URL, echo=False)
    TestSession = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with TestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()
